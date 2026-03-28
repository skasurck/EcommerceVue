from django.urls import path
from .views import MercadoPagoPreferenceView, MercadoPagoWebhookView

urlpatterns = [
    path('mercadopago/preferencias/', MercadoPagoPreferenceView.as_view(), name='mercadopago-preference'),
    path('mercadopago/webhook/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
]
