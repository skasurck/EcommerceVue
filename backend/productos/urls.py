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
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'atributos-base', AtributoViewSet)
router.register(r'atributos', ValorAtributoViewSet)
router.register(r'precios-escalonados', PrecioEscalonadoViewSet)

urlpatterns = [
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
]
