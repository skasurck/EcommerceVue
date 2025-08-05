from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
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
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs.order_by("-creado")

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
