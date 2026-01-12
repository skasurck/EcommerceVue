from django.db import models
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.utils.text import slugify
import os

# ──────────── CATEGORÍAS ────────────
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias'
    )

    class Meta:
        # Unicidad de slug por nivel (el slug debe ser único para un mismo padre)
        unique_together = (('slug', 'parent'),)
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        path = [self.nombre]
        parent = self.parent
        while parent is not None:
            path.insert(0, parent.nombre)
            parent = parent.parent
        return ' > '.join(path)

    def clean(self):
        """
        Validaciones del modelo.
        """
        super().clean()
        # --- VALIDACIÓN ANTI-CICLOS ---
        if self.parent:
            parent = self.parent
            # Recorremos los ancestros para asegurar que esta instancia no es uno de ellos.
            while parent is not None:
                if parent == self:
                    raise ValidationError(
                        "Error de jerarquía: Una categoría no puede ser su propia subcategoría (ciclo detectado)."
                    )
                parent = parent.parent

    def save(self, *args, **kwargs):
        """
        Sobrescribimos para auto-generar el slug y ejecutar validaciones.
        """
        if not self.slug:
            self.slug = slugify(self.nombre)
            # Aseguramos la unicidad del slug DENTRO DEL MISMO NIVEL
            original_slug = self.slug
            queryset = Categoria.objects.filter(slug=self.slug, parent=self.parent).exclude(pk=self.pk)
            count = 1
            while queryset.exists():
                self.slug = f"{original_slug}-{count}"
                queryset = Categoria.objects.filter(slug=self.slug, parent=self.parent).exclude(pk=self.pk)
                count += 1
        
        # Ejecutamos las validaciones del método clean() antes de guardar.
        self.full_clean()
        super().save(*args, **kwargs)

# ──────────── MARCAS ────────────
class Marca(models.Model):
    nombre = models.CharField(max_length=150, db_index=True)

    class Meta:
        ordering = ["nombre", "id"]  # agrega un campo único al final para estabilidad

    def __str__(self):
        return self.nombre

# ──────────── ATRIBUTOS ────────────
class Atributo(models.Model):
    nombre = models.CharField(max_length=150, db_index=True)
    class Meta:
        ordering = ["nombre", "id"]
    def __str__(self):
        return self.nombre

class ValorAtributo(models.Model):
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE, related_name="valores")
    valor = models.CharField(max_length=150, db_index=True)

    class Meta:
        ordering = ["valor", "id"]
        # evita duplicados globales del tipo (RAM, 8GB) repetidos
        constraints = [
            models.UniqueConstraint(fields=["atributo", "valor"], name="uniq_atributo_valor")
        ]

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
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    atributos = models.ManyToManyField(ValorAtributo, blank=True)
    stock = models.PositiveIntegerField(default=0)
    category_ai_main = models.CharField(max_length=64, null=True, blank=True)
    category_ai_sub = models.CharField(max_length=64, null=True, blank=True)
    category_ai_conf_main = models.FloatField(null=True, blank=True)
    category_ai_conf_sub = models.FloatField(null=True, blank=True)
    fecha_clasificacion_ai = models.DateTimeField(null=True, blank=True, help_text="Fecha de la última clasificación por IA.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_imagen = None
        old_miniatura = None

        if not is_new:
            try:
                old = Producto.objects.only('imagen_principal', 'miniatura').get(pk=self.pk)
                old_imagen = old.imagen_principal
                old_miniatura = old.miniatura
            except Producto.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Validación automática del estado de inventario según el stock
        if self.stock == 0 and self.estado_inventario != 'agotado':
            self.estado_inventario = 'agotado'
            super().save(update_fields=['estado_inventario'])
        elif self.stock > 0 and self.estado_inventario != 'en_existencia':
            self.estado_inventario = 'en_existencia'
            super().save(update_fields=['estado_inventario'])

        regenerate = False
        if self.imagen_principal:
            if is_new or self.imagen_principal != old_imagen or not old_miniatura:
                regenerate = True

        if regenerate:
            try:
                # Asegurarse de abrir desde la ruta final en disco
                self.imagen_principal.open()
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

    def __str__(self):
        return self.nombre

# ──────────── GALERÍA DE IMÁGENES ────────────
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='galeria', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/galeria/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

    def vista_previa(self):
        if self.imagen:
            return format_html('<img src="{}" width="60" height="60" />', self.imagen.url)
        return "Sin imagen"

    vista_previa.short_description = "Vista previa"

    def delete(self, *args, **kwargs):
        if self.imagen:
            self.imagen.delete(save=False)
        super().delete(*args, **kwargs)

# ──────────── PRECIOS ESCALONADOS ────────────
class PrecioEscalonado(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_escalonados')
    cantidad_minima = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'cantidad_minima')

    def __str__(self):
        return f"{self.producto.nombre} - desde {self.cantidad_minima} u. a ${self.precio_unitario} c/u"
