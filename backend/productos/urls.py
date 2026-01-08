from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductClassificationAPIView,
    ProductClassificationStatusView,
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
    BulkApplyCategoryAPIView,
    PriceRangeAPIView,
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'marcas', MarcaViewSet, basename='marcas')
router.register(r'atributos-base', AtributoViewSet, basename='atributos-base')
router.register(r'atributos', ValorAtributoViewSet, basename='atributos')

urlpatterns = [
    path('ai/pending-review/', PendingReviewProductsAPIView.as_view(), name='ai-pending-review'),
    path('all-categories/', AllCategoriesAPIView.as_view(), name='all-categories'),
    path('productos/<int:pk>/apply-category/', ApplyCategoryAPIView.as_view(), name='producto-apply-category'),
    path('productos/bulk-apply-category/', BulkApplyCategoryAPIView.as_view(), name='producto-bulk-apply-category'),
    path('ai/classify-products/', ProductClassificationAPIView.as_view(), name='ai-classify-products'),
    path('ai/classify-products/status/<str:task_id>/', ProductClassificationStatusView.as_view(), name='ai-classify-status'),
    path('price-range/', PriceRangeAPIView.as_view(), name='price-range'),
    path('search/products/', ProductSearchAPIView.as_view(), name='product-search'),

    # Rutas del router (list, retrieve, create, update, delete)
    path('', include(router.urls)),

    # Galería anidada bajo producto
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

    # Precios escalonados anidados bajo producto
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
