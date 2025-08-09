from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Sum, Avg
from django.utils.dateparse import parse_date
from .models import Direccion, MetodoEnvio, Pedido
from .serializers import DireccionSerializer, MetodoEnvioSerializer, PedidoSerializer
from usuarios.permissions import IsAdminOrSuperAdmin


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Direccion.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "tiene_direccion": queryset.exists(),
            "direcciones": serializer.data,
        })

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = instance.user
        was_default = instance.predeterminada
        super().perform_destroy(instance)
        if was_default:
            restante = Direccion.objects.filter(user=user).first()
            if restante:
                Direccion.objects.filter(user=user).update(predeterminada=False)
                restante.predeterminada = True
                restante.save(update_fields=["predeterminada"])


class MetodoEnvioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetodoEnvio.objects.all()
    serializer_class = MetodoEnvioSerializer
    permission_classes = [permissions.AllowAny]


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'direccion__nombre', 'direccion__apellidos', 'direccion__email']
    ordering_fields = ['creado', 'total']
    ordering = ['-creado']

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Pedido.objects.all()
            if hasattr(user, "perfil") and user.perfil.rol in ("admin", "super_admin")
            else Pedido.objects.filter(user=user)
        )
        params = self.request.query_params
        estado = params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        fecha_desde = params.get("fecha_desde")
        if fecha_desde:
            qs = qs.filter(creado__date__gte=parse_date(fecha_desde))
        fecha_hasta = params.get("fecha_hasta")
        if fecha_hasta:
            qs = qs.filter(creado__date__lte=parse_date(fecha_hasta))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError:
            raise
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_update_estado(self, request):
        ids = request.data.get('ids', [])
        estado = request.data.get('estado')
        allowed = ['pendiente', 'pagado', 'confirmado', 'enviado', 'cancelado']
        if estado not in allowed:
            return Response({'detail': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.estado = estado
                pedido.save(update_fields=['estado'])
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})


class ClienteSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]

    def get(self, request, user_id=None):
        email = request.query_params.get('email')
        if user_id:
            qs = Pedido.objects.filter(user_id=user_id)
        elif email:
            qs = Pedido.objects.filter(direccion__email=email)
        else:
            return Response({'detail': 'user_id o email requerido'}, status=status.HTTP_400_BAD_REQUEST)
        agg = qs.aggregate(total_spent=Sum('total'))
        orders_count = qs.count()
        total_spent = agg['total_spent'] or 0
        avg_ticket = total_spent / orders_count if orders_count else 0
        return Response({
            'orders_count': orders_count,
            'total_spent': f"{total_spent:.2f}",
            'avg_ticket': f"{avg_ticket:.2f}"
        })
