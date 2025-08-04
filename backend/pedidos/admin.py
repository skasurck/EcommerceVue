from django.contrib import admin
from .models import Direccion, MetodoEnvio, Pedido, PedidoItem, PedidoHistorial


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellidos", "calle", "ciudad", "estado")


@admin.register(MetodoEnvio)
class MetodoEnvioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "costo")


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0


class PedidoHistorialInline(admin.TabularInline):
    model = PedidoHistorial
    extra = 0
    readonly_fields = ("fecha", "descripcion")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "metodo_envio", "metodo_pago", "estado", "total", "creado")
    inlines = [PedidoItemInline, PedidoHistorialInline]
