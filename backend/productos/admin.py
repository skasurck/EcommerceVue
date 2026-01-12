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
    list_display = ('miniatura_preview','nombre', 'precio_normal', 'precio_rebajado', 'stock', 'estado_inventario')
    list_filter = ('estado', 'visibilidad', 'estado_inventario', 'categorias', 'marca')
    search_fields = ('nombre', 'sku')
    readonly_fields = ('miniatura_preview', 'imagen_principal_preview')
    inlines = [PrecioEscalonadoInline, ImagenProductoInline]  # 👈 Añade ambos aquí

    def miniatura_preview(self, obj):
        print("MINIATURA URL:", obj.miniatura.url if obj.miniatura else "NO HAY")
        if obj.miniatura and hasattr(obj.miniatura, 'url'):
            return format_html('<img src="{}" width="50" height="50" />', obj.miniatura.url)
        return "Sin miniatura"
    
    miniatura_preview.short_description = 'Miniatura'
    
    def imagen_principal_preview(self, obj):
        if obj.imagen_principal and hasattr(obj.imagen_principal, 'url'):
            return format_html('<img src="{}" width="100" height="100" />', obj.imagen_principal.url)
        return "Sin imagen principal"

    imagen_principal_preview.short_description = 'Imagen Principal'
# Registro de modelos individuales
admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Atributo)
admin.site.register(ValorAtributo)
admin.site.register(ImagenProducto)  