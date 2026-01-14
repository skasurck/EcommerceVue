from django import forms
from django.forms import inlineformset_factory
from .models import Producto, PrecioEscalonado, ValorAtributo

class ProductoForm(forms.ModelForm):
    eliminar_imagen = forms.BooleanField(required=False, label="Eliminar imagen actual")

    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion_corta',
            'descripcion_larga',
            'precio_normal',
            'precio_rebajado',
            'sku',
            'imagen_principal',
            'categoria',
            'categorias',
            'marca',
            'stock',
            'estado_inventario',
            'disponible',
            'visibilidad',
            'estado',
        ]
        widgets = {
            'descripcion_corta': forms.Textarea(attrs={'rows': 3}),
            'descripcion_larga': forms.Textarea(attrs={'rows': 5}),
            'categorias': forms.CheckboxSelectMultiple(),
        }


PrecioEscalonadoFormSet = inlineformset_factory(
    Producto,
    PrecioEscalonado,
    fields=['cantidad_minima', 'precio_unitario'],
    extra=0,
    can_delete=True,
)
