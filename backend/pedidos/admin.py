from django.contrib import admin
from .models import Direccion, MetodoEnvio, Pedido


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellidos", "calle", "ciudad", "estado")


@admin.register(MetodoEnvio)
class MetodoEnvioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "costo")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "metodo_envio", "metodo_pago", "creado")
