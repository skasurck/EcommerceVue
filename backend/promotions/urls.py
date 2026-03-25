# promotions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CuponViewSet, PromotionSettingsView, RunDailyOffersCommandView

router = DefaultRouter()
router.register('cupones', CuponViewSet, basename='cupon')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/', PromotionSettingsView.as_view(), name='promotion-settings'),
    path('run-daily-offers/', RunDailyOffersCommandView.as_view(), name='run-daily-offers'),
]
