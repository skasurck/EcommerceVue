from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import DireccionViewSet, MetodoEnvioViewSet, PedidoViewSet, ClienteSummaryView

router = DefaultRouter()
router.register('direcciones', DireccionViewSet, basename='direccion')
router.register('metodos-envio', MetodoEnvioViewSet, basename='metodoenvio')
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = router.urls + [
    path('clientes/<int:user_id>/summary/', ClienteSummaryView.as_view(), name='cliente-summary'),
    path('clientes/summary/', ClienteSummaryView.as_view(), name='cliente-summary-email'),
]
