from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Producto, Categoria, Marca, ValorAtributo
from .serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    MarcaSerializer,
    ValorAtributoSerializer,
)
from usuarios.permissions import IsAdminOrSuperAdmin

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('-fecha_creacion')
    serializer_class = ProductoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        categoria = self.request.query_params.get('categoria')
        estado = self.request.query_params.get('estado_inventario')
        marca = self.request.query_params.get('marca')

        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(sku__icontains=search))
        if categoria:
            queryset = queryset.filter(categorias__id=categoria)
        if estado:
            queryset = queryset.filter(estado_inventario=estado)
        if marca:
            queryset = queryset.filter(marca_id=marca)
        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class ValorAtributoViewSet(viewsets.ModelViewSet):
    queryset = ValorAtributo.objects.all()
    serializer_class = ValorAtributoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]
