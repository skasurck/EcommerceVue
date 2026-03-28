from django.urls import path
from .views import (
    MercadoPagoPreferenceView,
    MercadoPagoWebhookView,
    PlacesAutocompleteView,
    PlacesDetailsView,
)

urlpatterns = [
    path('mercadopago/preferencias/', MercadoPagoPreferenceView.as_view(), name='mercadopago-preference'),
    path('mercadopago/webhook/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),
    path('places/autocomplete/', PlacesAutocompleteView.as_view(), name='places-autocomplete'),
    path('places/details/', PlacesDetailsView.as_view(), name='places-details'),
]
