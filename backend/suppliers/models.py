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

class ProductSupplierMap(models.Model):
    product = models.ForeignKey(
        'productos.Producto',     # usa el app label y nombre real de tu modelo
        on_delete=models.CASCADE,
        related_name='supplier_links'
    )
    supplier = models.CharField(max_length=50, default="supermex")
    supplier_sku = models.CharField(max_length=64, unique=True)
    auto_hide_when_oos = models.BooleanField(default=True)