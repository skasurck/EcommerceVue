from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet
from .views import RegisterView

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
