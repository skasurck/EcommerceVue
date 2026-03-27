import logging
from django.db import models
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.utils.text import slugify
import os

logger = logging.getLogger(__name__)

# ──────────── CATEGORÍAS ────────────
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
    # 2. AÑADE ESTA CLASE META
    class Meta:
        # Esto asegura que el slug sea único para cada nivel de categoría padre.
        unique_together = ('slug', 'parent')
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

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
    nombre = models.CharField(max_length=100, db_index=True)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    precio_normal = models.DecimalField(max_digits=10, decimal_places=2)
    precio_rebajado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    imagen_principal = models.ImageField(upload_to='productos/', null=True, blank=True)
    miniatura = models.ImageField(upload_to='productos/miniaturas/', null=True, blank=True, editable=False)
    disponible = models.BooleanField(default=True)
    estado_inventario = models.CharField(max_length=20, choices=[
        ('en_existencia', 'En existencia'),
        ('agotado', 'Agotado')
    ], default='en_existencia', db_index=True)
    visibilidad = models.BooleanField(default=True, db_index=True)
    estado = models.CharField(max_length=20, choices=[
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado')
    ], default='borrador', db_index=True)
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    atributos = models.ManyToManyField(ValorAtributo, blank=True)
    stock = models.PositiveIntegerField(default=0)
    category_ai_main = models.CharField(max_length=64, null=True, blank=True)
    category_ai_sub = models.CharField(max_length=64, null=True, blank=True)
    category_ai_conf_main = models.FloatField(null=True, blank=True)
    category_ai_conf_sub = models.FloatField(null=True, blank=True)
    fecha_clasificacion_ai = models.DateTimeField(null=True, blank=True, help_text="Fecha de la última clasificación por IA.")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        reprocess_image = kwargs.pop('reprocess_image', False)

        # Guardar una copia del nombre de archivo original antes de que se modifique
        old_instance = None
        if self.pk:
            try:
                old_instance = Producto.objects.get(pk=self.pk)
            except Producto.DoesNotExist:
                pass

        # Lógica de negocio (ej. estado de inventario)
        if self.stock == 0 and self.estado_inventario != 'agotado':
            self.estado_inventario = 'agotado'
        elif self.stock > 0 and self.estado_inventario != 'en_existencia':
            self.estado_inventario = 'en_existencia'

        # Determinar si la imagen debe ser procesada
        image_has_changed_on_model = (old_instance and old_instance.imagen_principal != self.imagen_principal)
        is_new_image = (self.pk is None and self.imagen_principal)
        force_reprocess = reprocess_image and self.imagen_principal

        # La condición principal para procesar la imagen
        if is_new_image or image_has_changed_on_model or force_reprocess:
            
            # Evitar reprocesar si ya es WebP, a menos que sea una imagen nueva o cambiada
            if force_reprocess and not image_has_changed_on_model and 'webp' in self.imagen_principal.name.lower():
                pass # Ya es WebP y no ha cambiado, no hacer nada.
            else:
                try:
                    self.imagen_principal.open()
                    with Image.open(self.imagen_principal) as img:
                        img.load()  # cargar datos antes de cerrar el archivo

                    original_filename = self.imagen_principal.name
                    base_name = os.path.splitext(os.path.basename(original_filename))[0]

                    # --- Convertir imagen principal a WebP ---
                    buffer_main = BytesIO()
                    img.save(buffer_main, format='WEBP', quality=85)
                    main_file = ContentFile(buffer_main.getvalue())
                    filename_main = f"{slugify(base_name)}_{get_random_string(7)}.webp"

                    # --- Generar miniatura WebP ---
                    thumb_img = img.copy()
                    thumb_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    
                    # Corregir manejo de transparencia para la miniatura
                    if thumb_img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', thumb_img.size, (255, 255, 255))
                        # Usar el canal alfa como máscara para preservar la transparencia sobre el fondo blanco
                        if 'A' in thumb_img.mode:
                            background.paste(thumb_img, mask=thumb_img.split()[-1])
                        else: # Para modo 'P' con paleta de transparencia
                            background.paste(thumb_img)
                        thumb_img = background

                    buffer_thumb = BytesIO()
                    thumb_img.save(buffer_thumb, format='WEBP', quality=80)
                    thumb_file = ContentFile(buffer_thumb.getvalue())
                    filename_thumb = f"{slugify(base_name)}_thumbnail.webp"

                    # Eliminar la imagen principal antigua si ha cambiado
                    if image_has_changed_on_model and old_instance and old_instance.imagen_principal:
                        old_instance.imagen_principal.delete(save=False)
                    
                    # Eliminar la miniatura antigua si existía
                    if old_instance and old_instance.miniatura:
                        old_instance.miniatura.delete(save=False)
                    
                    # Guardar los nuevos archivos. `save=False` evita la recursión.
                    self.imagen_principal.save(filename_main, main_file, save=False)
                    self.miniatura.save(filename_thumb, thumb_file, save=False)
                
                except (OSError, Image.UnidentifiedImageError) as e:
                    logger.exception("Error procesando la imagen del producto %s: %s", self.pk, e)

        # Si la imagen se eliminó del producto, eliminar los archivos asociados
        elif old_instance and old_instance.imagen_principal and not self.imagen_principal:
            old_instance.imagen_principal.delete(save=False)
            if old_instance.miniatura:
                old_instance.miniatura.delete(save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class ProductClassificationFeedback(models.Model):
    SOURCE_MANUAL_SINGLE = "manual_single"
    SOURCE_MANUAL_BULK = "manual_bulk"
    SOURCE_CHOICES = (
        (SOURCE_MANUAL_SINGLE, "Manual single"),
        (SOURCE_MANUAL_BULK, "Manual bulk"),
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classification_feedback",
    )
    input_text = models.TextField()
    target_main = models.CharField(max_length=128, db_index=True)
    target_sub = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES, default=SOURCE_MANUAL_SINGLE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.target_main} | {self.target_sub}"

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

    def save(self, *args, **kwargs):
        reprocess_image = kwargs.pop('reprocess_image', False)

        old_instance = None
        if self.pk:
            try:
                old_instance = ImagenProducto.objects.get(pk=self.pk)
            except ImagenProducto.DoesNotExist:
                pass

        image_has_changed = (old_instance and old_instance.imagen != self.imagen)
        is_new = self.pk is None
        should_process_image = (is_new and self.imagen) or image_has_changed or (reprocess_image and self.imagen)

        if should_process_image:
            if reprocess_image and not image_has_changed and self.imagen and 'webp' in self.imagen.name.lower():
                pass  # Ya es WebP y no ha cambiado, no hacer nada.
            else:
                try:
                    self.imagen.open()
                    img = Image.open(self.imagen)
                    
                    base_name = os.path.splitext(os.path.basename(self.imagen.name))[0]

                    buffer = BytesIO()
                    img.save(buffer, format='WEBP', quality=85)
                    file_content = ContentFile(buffer.getvalue())
                    filename = f"{slugify(base_name)}_{get_random_string(7)}.webp"
                    
                    # Eliminar archivo antiguo solo si la imagen ha cambiado
                    if image_has_changed and old_instance and old_instance.imagen:
                        old_instance.imagen.delete(save=False)
                    
                    self.imagen.save(filename, file_content, save=False)
                
                except Exception as e:
                    print(f"Error procesando la imagen de la galería {self.pk}: {e}")

        super().save(*args, **kwargs)

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


class HomeSliderImage(models.Model):
    titulo = models.CharField(max_length=120, blank=True, default="")
    descripcion = models.CharField(max_length=255, blank=True, default="")
    imagen = models.ImageField(upload_to="home_slider/")
    titulo_color = models.CharField(max_length=7, blank=True, default="#ea580c")
    titulo_mobile = models.CharField(max_length=120, blank=True, default="")
    descripcion_mobile = models.CharField(max_length=255, blank=True, default="")
    imagen_mobile = models.ImageField(upload_to="home_slider/mobile/", null=True, blank=True)
    orden = models.PositiveIntegerField(default=0, db_index=True)
    activo = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "id"]

    def __str__(self):
        return self.titulo or f"Slide #{self.pk}"

    def _convert_to_webp(self, field, upload_to):
        """Convierte el campo de imagen a WebP y lo guarda en el campo."""
        try:
            field.open()
            with Image.open(field) as img:
                img.load()
            base_name = os.path.splitext(os.path.basename(field.name))[0]
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if 'A' in img.mode:
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=85)
            filename = f"{slugify(base_name)}_{get_random_string(7)}.webp"
            field.save(filename, ContentFile(buffer.getvalue()), save=False)
        except Exception as e:
            logger.exception("Error convirtiendo imagen a WebP en %s: %s", self.__class__.__name__, e)

    def save(self, *args, **kwargs):
        old_instance = None
        if self.pk:
            try:
                old_instance = HomeSliderImage.objects.get(pk=self.pk)
            except HomeSliderImage.DoesNotExist:
                pass

        # Procesar imagen desktop
        imagen_changed = old_instance and old_instance.imagen != self.imagen
        if (self.pk is None and self.imagen) or imagen_changed:
            if imagen_changed and old_instance.imagen:
                old_instance.imagen.delete(save=False)
            if not self.imagen.name.lower().endswith('.webp'):
                self._convert_to_webp(self.imagen, 'home_slider/')

        # Procesar imagen mobile
        imagen_mobile_changed = old_instance and old_instance.imagen_mobile != self.imagen_mobile
        if (self.pk is None and self.imagen_mobile) or imagen_mobile_changed:
            if imagen_mobile_changed and old_instance.imagen_mobile:
                old_instance.imagen_mobile.delete(save=False)
            if self.imagen_mobile and not self.imagen_mobile.name.lower().endswith('.webp'):
                self._convert_to_webp(self.imagen_mobile, 'home_slider/mobile/')

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.imagen:
            self.imagen.delete(save=False)
        if self.imagen_mobile:
            self.imagen_mobile.delete(save=False)
        super().delete(*args, **kwargs)


# ──────────── PRODUCTOS DESTACADOS ────────────
class ProductoDestacado(models.Model):
    TIPO_MANUAL = 'manual'
    TIPO_AUTO = 'automatico'
    TIPO_CHOICES = [
        (TIPO_MANUAL, 'Manual'),
        (TIPO_AUTO, 'Automático'),
    ]

    MOTIVO_CAMPANA = 'campana'
    MOTIVO_VENTAS = 'ventas'
    MOTIVO_NOVEDAD = 'novedad'
    MOTIVO_OFERTA = 'oferta'
    MOTIVO_CHOICES = [
        (MOTIVO_CAMPANA, 'Destacado manual por campaña'),
        (MOTIVO_VENTAS, 'Destacado automático por ventas'),
        (MOTIVO_NOVEDAD, 'Destacado automático por novedad'),
        (MOTIVO_OFERTA, 'Destacado automático por oferta'),
    ]

    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name='destacado',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_MANUAL,
        db_index=True,
    )
    activo = models.BooleanField(default=True, db_index=True)
    prioridad = models.PositiveIntegerField(
        default=0,
        help_text="Menor número = más prioritario. Solo aplica para tipo manual.",
    )
    fecha_inicio = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha desde la que el destacado es válido. Null = siempre.",
    )
    fecha_fin = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha de vencimiento opcional. Null = sin vencimiento.",
    )
    bloqueado = models.BooleanField(
        default=False,
        help_text="Si está activo, el algoritmo automático no modificará este registro.",
    )
    puntaje_auto = models.FloatField(
        null=True, blank=True,
        help_text="Puntaje calculado por el algoritmo automático.",
    )
    motivo = models.CharField(
        max_length=50,
        choices=MOTIVO_CHOICES,
        null=True, blank=True,
        help_text="Razón principal del destacado.",
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['prioridad', '-puntaje_auto', 'id']
        verbose_name = 'Producto Destacado'
        verbose_name_plural = 'Productos Destacados'

    def __str__(self):
        return f"Destacado ({self.tipo}): {self.producto.nombre}"


# ──────────── LISTA DE DESEOS ────────────
class ListaDeseos(models.Model):
    from django.contrib.auth import get_user_model
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='lista_deseos'
    )
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='en_lista_deseos'
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')
        ordering = ['-fecha_agregado']

    def __str__(self):
        return f"{self.usuario.username} → {self.producto.nombre}"


class PromoBanner(models.Model):
    titulo = models.CharField(max_length=120, blank=True, default="")
    descripcion = models.CharField(max_length=255, blank=True, default="")
    imagen = models.ImageField(upload_to="promo_banners/")
    titulo_color = models.CharField(max_length=7, blank=True, default="#ffffff")
    enlace = models.CharField(max_length=500, blank=True, default="")
    orden = models.PositiveIntegerField(default=0, db_index=True)
    activo = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "id"]

    def __str__(self):
        return self.titulo or f"Banner #{self.pk}"

    def save(self, *args, **kwargs):
        old_instance = None
        if self.pk:
            try:
                old_instance = PromoBanner.objects.get(pk=self.pk)
            except PromoBanner.DoesNotExist:
                pass

        imagen_changed = old_instance and old_instance.imagen != self.imagen
        if (self.pk is None and self.imagen) or imagen_changed:
            if imagen_changed and old_instance.imagen:
                old_instance.imagen.delete(save=False)
            if not self.imagen.name.lower().endswith('.webp'):
                try:
                    self.imagen.open()
                    with Image.open(self.imagen) as img:
                        img.load()
                    base_name = os.path.splitext(os.path.basename(self.imagen.name))[0]
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if 'A' in img.mode:
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    buffer = BytesIO()
                    img.save(buffer, format='WEBP', quality=85)
                    filename = f"{slugify(base_name)}_{get_random_string(7)}.webp"
                    self.imagen.save(filename, ContentFile(buffer.getvalue()), save=False)
                except Exception as e:
                    logger.exception("Error convirtiendo imagen de banner a WebP: %s", e)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.imagen:
            self.imagen.delete(save=False)
        super().delete(*args, **kwargs)
