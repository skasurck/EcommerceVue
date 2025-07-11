
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from .models import Producto
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
