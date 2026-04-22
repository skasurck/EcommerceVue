from django.urls import path

from .views import (
    ConsentimientoAPIView,
    EventoTrackingAPIView,
    MisDatosTrackingAPIView,
)

urlpatterns = [
    path('eventos/', EventoTrackingAPIView.as_view(), name='tracking-eventos'),
    path('consentimiento/', ConsentimientoAPIView.as_view(), name='tracking-consentimiento'),
    path('mis-datos/', MisDatosTrackingAPIView.as_view(), name='tracking-mis-datos'),
]
