from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Sum, Avg
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import Direccion, MetodoEnvio, Pedido, PedidoHistorial
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
        if self.action == "create":
            return [permissions.AllowAny()]
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
        papelera = params.get("papelera")
        incluye_papelera = params.get("incluye_papelera")
        if papelera:
            qs = qs.filter(papelera=True)
        elif not incluye_papelera:
            qs = qs.filter(papelera=False)
        fecha_desde = params.get("fecha_desde")
        if fecha_desde:
            qs = qs.filter(creado__date__gte=parse_date(fecha_desde))
        fecha_hasta = params.get("fecha_hasta")
        if fecha_hasta:
            qs = qs.filter(creado__date__lte=parse_date(fecha_hasta))
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

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

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def trash(self, request, pk=None):
        pedido = self.get_object()
        if pedido.papelera:
            return Response({'detail': 'Ya está en papelera'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.papelera = True
        pedido.eliminado_en = timezone.now()
        pedido.save(update_fields=['papelera', 'eliminado_en'])
        PedidoHistorial.objects.create(pedido=pedido, descripcion='Movido a papelera')
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def restore(self, request, pk=None):
        pedido = self.get_object()
        if not pedido.papelera:
            return Response({'detail': 'Pedido no está en papelera'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.papelera = False
        pedido.eliminado_en = None
        pedido.save(update_fields=['papelera', 'eliminado_en'])
        PedidoHistorial.objects.create(pedido=pedido, descripcion='Restaurado desde papelera')
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_trash(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.papelera = True
                pedido.eliminado_en = timezone.now()
                pedido.save(update_fields=['papelera', 'eliminado_en'])
                PedidoHistorial.objects.create(pedido=pedido, descripcion='Movido a papelera')
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_restore(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.papelera = False
                pedido.eliminado_en = None
                pedido.save(update_fields=['papelera', 'eliminado_en'])
                PedidoHistorial.objects.create(pedido=pedido, descripcion='Restaurado desde papelera')
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_destroy(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                if not pedido.papelera:
                    raise Exception('No está en papelera')
                pedido.delete()
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.papelera:
            return Response({'detail': 'Debe estar en papelera para eliminar'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
