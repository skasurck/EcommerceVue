from django.contrib import admin
from .models import Cupon, DailyOffer, PromotionSettings


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'valor', 'activo', 'fecha_inicio', 'fecha_fin', 'usos_actuales', 'usos_maximos']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo', 'descripcion']
    readonly_fields = ['usos_actuales']


@admin.register(DailyOffer)
class DailyOfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'sale_price', 'original_price', 'start_date', 'end_date', 'is_active']


@admin.register(PromotionSettings)
class PromotionSettingsAdmin(admin.ModelAdmin):
    pass
