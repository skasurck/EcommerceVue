# promotions/models.py
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from suppliers.models import SupplierProduct


class Cupon(models.Model):
    TIPO_PORCENTAJE = 'porcentaje'
    TIPO_MONTO_FIJO = 'monto_fijo'
    TIPO_CHOICES = [
        (TIPO_PORCENTAJE, 'Porcentaje'),
        (TIPO_MONTO_FIJO, 'Monto fijo'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_PORCENTAJE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    usos_maximos = models.PositiveIntegerField(null=True, blank=True, help_text='Vacío = ilimitado')
    usos_actuales = models.PositiveIntegerField(default=0)
    monto_minimo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Monto mínimo de compra requerido. Vacío = sin mínimo'
    )

    class Meta:
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'
        ordering = ['-id']

    def __str__(self):
        return f'{self.codigo} ({self.get_tipo_display()} {self.valor})'

    def es_valido(self, subtotal=Decimal('0')):
        """Verifica si el cupón puede aplicarse. Retorna (ok, mensaje)."""
        if not self.activo:
            return False, 'El cupón no está activo.'
        ahora = timezone.now()
        if self.fecha_inicio and ahora < self.fecha_inicio:
            return False, 'El cupón aún no está vigente.'
        if self.fecha_fin and ahora > self.fecha_fin:
            return False, 'El cupón ha expirado.'
        if self.usos_maximos is not None and self.usos_actuales >= self.usos_maximos:
            return False, 'El cupón ha alcanzado el límite de usos.'
        if self.monto_minimo and subtotal < self.monto_minimo:
            return False, f'El monto mínimo para este cupón es ${self.monto_minimo}.'
        return True, ''

    def calcular_descuento(self, subtotal):
        """Calcula el monto de descuento a aplicar sobre el subtotal."""
        if self.tipo == self.TIPO_PORCENTAJE:
            return (subtotal * self.valor / Decimal('100')).quantize(Decimal('0.01'))
        return min(self.valor, subtotal)

class DailyOffer(models.Model):
    """
    Represents a daily offer for a specific product.
    """
    product = models.ForeignKey(
        SupplierProduct, 
        on_delete=models.CASCADE, 
        related_name='daily_offers'
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The discounted price for the offer."
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The price of the product before the discount was applied."
    )
    start_date = models.DateTimeField(
        help_text="The date and time when the offer starts."
    )
    end_date = models.DateTimeField(
        help_text="The date and time when the offer ends."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the offer is currently active."
    )

    def clean(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'end_date debe ser posterior a start_date.'})

    def __str__(self):
        return f"Offer for {self.product.name} at ${self.sale_price}"

    class Meta:
        ordering = ['-start_date']


class PromotionSettings(models.Model):
    """
    A singleton model to hold global settings for the promotions system.
    """
    daily_offers_enabled = models.BooleanField(
        default=False,
        help_text="Enable or disable the automatic creation of daily offers."
    )

    def __str__(self):
        return "Promotion Settings"

    def save(self, *args, **kwargs):
        """Enforce a single instance of this model."""
        self.pk = 1
        super(PromotionSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the singleton instance, creating it if it doesn't exist."""
        with transaction.atomic():
            obj, created = cls.objects.select_for_update().get_or_create(pk=1)
        return obj