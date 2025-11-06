# promotions/urls.py
from django.urls import path
from .views import PromotionSettingsView, RunDailyOffersCommandView

urlpatterns = [
    path('settings/', PromotionSettingsView.as_view(), name='promotion-settings'),
    path('run-daily-offers/', RunDailyOffersCommandView.as_view(), name='run-daily-offers'),
]
