# suppliers/models.py
from django.db import models
from productos.models import Producto

class SupplierProduct(models.Model):
    supplier = models.CharField(max_length=50, default="supermex")
    supplier_sku = models.CharField(max_length=64, unique=True)
    product_url = models.URLField()
    name = models.CharField(max_length=255)
    description_html = models.TextField(blank=True)
    image_urls = models.JSONField(default=list)
    price_supplier = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    available_qty = models.IntegerField(default=0)     # <-- NUEVO
    last_seen = models.DateTimeField(auto_now=True)
    checksum = models.CharField(max_length=64, blank=True)
    # Caché de IDs de Odoo para llamadas AJAX directas (evita cargar HTML en sync de stock)
    odoo_product_id = models.IntegerField(null=True, blank=True)
    odoo_template_id = models.IntegerField(null=True, blank=True)
    # Control de productos discontinuados
    is_active = models.BooleanField(default=True, db_index=True)
    consecutive_404s = models.IntegerField(default=0)

class SupplierStockHistory(models.Model):
    """Snapshot diario de stock por producto. Permite estimar ventas como descensos de inventario."""
    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name='stock_history',
    )
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    available_qty = models.IntegerField()
    in_stock = models.BooleanField()

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['supplier_product', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.supplier_product.supplier_sku} @ {self.recorded_at:%Y-%m-%d %H:%M} qty={self.available_qty}"


class ProductSupplierMap(models.Model):
    product = models.ForeignKey(
        'productos.Producto',     # usa el app label y nombre real de tu modelo
        on_delete=models.CASCADE,
        related_name='supplier_links'
    )
    supplier = models.CharField(max_length=50, default="supermex")
    supplier_sku = models.CharField(max_length=64, unique=True)
    auto_hide_when_oos = models.BooleanField(default=True)