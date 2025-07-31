from rest_framework import viewsets
from .models import Producto, Categoria, Marca, ValorAtributo
from .serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    MarcaSerializer,
    ValorAtributoSerializer
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ValorAtributoViewSet(viewsets.ModelViewSet):
    queryset = ValorAtributo.objects.all()
    serializer_class = ValorAtributoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
