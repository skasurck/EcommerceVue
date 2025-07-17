from django.db import models
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
import os

# ──────────── CATEGORÍAS ────────────
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

# ──────────── MARCAS ────────────
class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# ──────────── ATRIBUTOS ────────────
class Atributo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ValorAtributo(models.Model):
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)
    valor = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"

# ──────────── PRODUCTOS ────────────
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)  # Se permite HTML desde el frontend
    precio_normal = models.DecimalField(max_digits=10, decimal_places=2)
    precio_rebajado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    imagen_principal = models.ImageField(upload_to='productos/', null=True, blank=True)
    miniatura = models.ImageField(upload_to='productos/miniaturas/', null=True, blank=True, editable=False)
    disponible = models.BooleanField(default=True)
    estado_inventario = models.CharField(max_length=20, choices=[
        ('en_existencia', 'En existencia'),
        ('agotado', 'Agotado')
    ], default='en_existencia')
    visibilidad = models.BooleanField(default=True)  # Público o privado
    estado = models.CharField(max_length=20, choices=[
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado')
    ], default='borrador')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    atributos = models.ManyToManyField(ValorAtributo, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Validación automática del estado de inventario según el stock
        if self.stock == 0 and self.estado_inventario != 'agotado':
            self.estado_inventario = 'agotado'
            super().save(update_fields=['estado_inventario'])
        elif self.stock > 0 and self.estado_inventario != 'en_existencia':
            self.estado_inventario = 'en_existencia'
            super().save(update_fields=['estado_inventario'])

        # Regenerar miniatura si hay imagen principal
        if self.imagen_principal:
            try:
                img = Image.open(self.imagen_principal)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                fondo = Image.new('RGB', (200, 200), (255, 255, 255))
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                x = (200 - img.width) // 2
                y = (200 - img.height) // 2
                fondo.paste(img, (x, y))

                buffer = BytesIO()
                fondo.save(buffer, format='JPEG')
                thumb_file = ContentFile(buffer.getvalue())

                self.miniatura.save(f'{self.pk}_miniatura.jpg', thumb_file, save=False)
                super().save(update_fields=['miniatura'])

                print(f"✅ MINIATURA GENERADA para producto {self.pk}")

            except Exception as e:
                print(f"[Error] No se pudo generar miniatura: {e}")

         # Solo genera miniatura si hay imagen y ya existe 
    def __str__(self):
        return self.nombre

# ──────────── GALERÍA DE IMÁGENES ────────────
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='galeria')
    imagen = models.ImageField(upload_to='productos/galeria/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

# ──────────── PRECIOS ESCALONADOS ────────────
class PrecioEscalonado(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_escalonados')
    cantidad_minima = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'cantidad_minima')

    def __str__(self):
        return f"{self.producto.nombre} - desde {self.cantidad_minima} u. a ${self.precio_unitario} c/u"
