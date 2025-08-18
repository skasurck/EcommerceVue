from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet,
    CategoriaViewSet,
    MarcaViewSet,
    AtributoViewSet,
    ValorAtributoViewSet,
    ImagenProductoViewSet,
    PrecioEscalonadoViewSet,
    ProductSearchAPIView,
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'atributos-base', AtributoViewSet)
router.register(r'atributos', ValorAtributoViewSet)

urlpatterns = [
    path('search/products/', ProductSearchAPIView.as_view(), name='product-search'),
    path('', include(router.urls)),
    path(
        'productos/<int:producto_pk>/galeria/',
        ImagenProductoViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='producto-galeria',
    ),
    path(
        'galeria/<int:pk>/',
        ImagenProductoViewSet.as_view({'delete': 'destroy'}),
        name='galeria-detalle',
    ),
    path(
        'productos/<int:producto_pk>/precios-escalonados/',
        PrecioEscalonadoViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='producto-precios-escalonados',
    ),
    path(
        'precios-escalonados/<int:pk>/',
        PrecioEscalonadoViewSet.as_view({'put': 'update', 'delete': 'destroy'}),
        name='precios-escalonados-detalle',
    ),
]
