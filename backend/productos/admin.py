from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Categoria, Marca, Atributo, ValorAtributo, ImagenProducto, PrecioEscalonado

class PrecioEscalonadoInline(admin.TabularInline):
    model = PrecioEscalonado
    extra = 1  # Número de líneas vacías por default
    min_num = 0
    can_delete = True

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    min_num = 0
    can_delete = True

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_normal', 'precio_rebajado', 'estado_inventario')
    list_filter = ('estado', 'visibilidad', 'estado_inventario', 'categoria', 'marca')
    search_fields = ('nombre', 'sku')
    readonly_fields = ('miniatura_preview',)
    inlines = [PrecioEscalonadoInline, ImagenProductoInline]  # 👈 Añade ambos aquí

    def miniatura_preview(self, obj):
        if obj.miniatura:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.miniatura.url)
        return "Sin miniatura"
    
    miniatura_preview.short_description = 'Miniatura'
# Registro de modelos individuales
admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Atributo)
admin.site.register(ValorAtributo)
