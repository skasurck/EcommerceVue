from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, MarcaViewSet, ValorAtributoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'atributos', ValorAtributoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
