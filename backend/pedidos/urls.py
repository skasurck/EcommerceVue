from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import DireccionViewSet, MetodoEnvioViewSet, PedidoViewSet, ClienteSummaryView, PedidoByPreferenceView, PedidoPublicView

router = DefaultRouter()
router.register('direcciones', DireccionViewSet, basename='direccion')
router.register('metodos-envio', MetodoEnvioViewSet, basename='metodoenvio')
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = router.urls + [
    path('pedidos/by-preference/<str:preference_id>/', PedidoByPreferenceView.as_view(), name='pedido-by-preference'),
    path('pedidos/public/<int:pedido_id>/', PedidoPublicView.as_view(), name='pedido-public'),
    path('clientes/<int:user_id>/summary/', ClienteSummaryView.as_view(), name='cliente-summary'),
    path('clientes/summary/', ClienteSummaryView.as_view(), name='cliente-summary-email'),
]
