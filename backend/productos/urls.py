from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductClassificationAPIView,
    ProductoViewSet,
    CategoriaViewSet,
    MarcaViewSet,
    AtributoViewSet,
    ValorAtributoViewSet,
    ImagenProductoViewSet,
    PrecioEscalonadoViewSet,
    ProductSearchAPIView,
    PendingReviewProductsAPIView,
    AllCategoriesAPIView,
    ApplyCategoryAPIView,
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'atributos-base', AtributoViewSet)
router.register(r'atributos', ValorAtributoViewSet)

urlpatterns = [
    path(
        'ai/pending-review/',
        PendingReviewProductsAPIView.as_view(),
        name='ai-pending-review',
    ),
    path(
        'all-categories/',
        AllCategoriesAPIView.as_view(),
        name='all-categories',
    ),
    path(
        'productos/<int:pk>/apply-category/',
        ApplyCategoryAPIView.as_view(),
        name='producto-apply-category',
    ),
    path('ai/classify-products/', ProductClassificationAPIView.as_view(), name='ai-classify-products'),
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
