from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import PrecioEscalonado, Producto


def clear_product_list_cache():
    cache.clear()


# Campos que, si son los únicos actualizados, no deben re-generar keywords
_SKIP_KEYWORD_FIELDS = frozenset({
    'search_keywords',
    'miniatura',
    'category_ai_main', 'category_ai_sub',
    'category_ai_conf_main', 'category_ai_conf_sub',
    'fecha_clasificacion_ai',
    'estado_inventario', 'stock',
    'visibilidad', 'estado',
})


@receiver(post_save, sender=Producto)
@receiver(post_delete, sender=Producto)
def product_changed(sender, instance=None, created=False, update_fields=None, **kwargs):
    clear_product_list_cache()

    # Generar keywords si:
    # - El producto es nuevo (created=True)
    # - O se editaron campos de contenido (nombre, descripcion, sku) y no tiene keywords
    # - Nunca cuando solo se actualizan campos técnicos/IA
    if instance is None:
        return

    # Si update_fields indica que solo se tocaron campos internos, ignorar
    if update_fields and set(update_fields).issubset(_SKIP_KEYWORD_FIELDS):
        return

    # Generar solo si no tiene keywords o si el producto es nuevo
    if created or not instance.search_keywords:
        from .tasks import generate_keywords_task
        generate_keywords_task.delay(instance.pk)


@receiver(post_save, sender=PrecioEscalonado)
@receiver(post_delete, sender=PrecioEscalonado)
def tier_changed(sender, **kwargs):
    clear_product_list_cache()


@receiver(m2m_changed, sender=Producto.atributos.through)
def product_attributes_changed(sender, **kwargs):
    clear_product_list_cache()
