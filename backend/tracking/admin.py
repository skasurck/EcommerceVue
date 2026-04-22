from django.contrib import admin

from .models import (
    AgregadoDiarioProducto,
    CoOcurrenciaProducto,
    ConsentimientoTracking,
    EventoUsuario,
)


@admin.register(EventoUsuario)
class EventoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'producto', 'usuario', 'visitor_id', 'created_at')
    list_filter = ('tipo', 'is_bot')
    search_fields = ('visitor_id', 'session_key', 'usuario__username', 'producto__nombre')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('producto', 'categoria', 'usuario')


@admin.register(AgregadoDiarioProducto)
class AgregadoDiarioProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'fecha', 'views', 'add_carts',
                    'wishlist_adds', 'purchases', 'clicks_rec', 'impressions_rec')
    list_filter = ('fecha',)
    date_hierarchy = 'fecha'
    autocomplete_fields = ('producto',)


@admin.register(CoOcurrenciaProducto)
class CoOcurrenciaProductoAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'fuente', 'score', 'actualizado')
    list_filter = ('fuente',)
    autocomplete_fields = ('origen', 'destino')


@admin.register(ConsentimientoTracking)
class ConsentimientoTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'visitor_id',
                    'acepta_analytics', 'acepta_personalizacion',
                    'version_aviso', 'updated_at')
    list_filter = ('acepta_analytics', 'acepta_personalizacion', 'version_aviso')
    search_fields = ('visitor_id', 'usuario__username')
