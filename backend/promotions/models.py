# promotions/models.py
from django.db import models
from suppliers.models import SupplierProduct

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
        obj, created = cls.objects.get_or_create(pk=1)
        return obj