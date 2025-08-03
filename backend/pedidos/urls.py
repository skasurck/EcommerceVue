from rest_framework.routers import DefaultRouter
from .views import DireccionViewSet, MetodoEnvioViewSet, PedidoViewSet

router = DefaultRouter()
router.register('direcciones', DireccionViewSet, basename='direccion')
router.register('metodos-envio', MetodoEnvioViewSet, basename='metodoenvio')
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = router.urls
