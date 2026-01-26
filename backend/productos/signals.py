from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import PrecioEscalonado, Producto


def clear_product_list_cache():
    # Simple invalidation: clears cached list responses.
    cache.clear()


@receiver(post_save, sender=Producto)
@receiver(post_delete, sender=Producto)
def product_changed(sender, **kwargs):
    clear_product_list_cache()


@receiver(post_save, sender=PrecioEscalonado)
@receiver(post_delete, sender=PrecioEscalonado)
def tier_changed(sender, **kwargs):
    clear_product_list_cache()


@receiver(m2m_changed, sender=Producto.atributos.through)
def product_attributes_changed(sender, **kwargs):
    clear_product_list_cache()
