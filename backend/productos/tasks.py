from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Producto
from .ai import build_text_from_product, classify_text
from django.db import transaction
from django.utils import timezone

logger = get_task_logger(__name__)

@shared_task(bind=True)
def classify_products_task(self, product_ids, overwrite=False):
    """
    Tarea asíncrona de Celery para clasificar productos.
    """
    total_products = len(product_ids)
    processed_count = 0
    results = []

    logger.info(f"Iniciando clasificación para {total_products} productos. Sobrescribir: {overwrite}")

    for product_id in product_ids:
        try:
            product = Producto.objects.get(pk=product_id)

            if product.category_ai_main and not overwrite:
                processed_count += 1
                logger.info(f"Saltando producto {product_id} (ya clasificado).")
                self.update_state(
                    state='PROGRESS',
                    meta={'current': processed_count, 'total': total_products, 'status': f'Procesando {product.nombre}'}
                )
                continue
            
            logger.info(f"Clasificando producto {product_id}: {product.nombre}")
            text = build_text_from_product(product)
            if not text:
                text = product.nombre or f"Producto {product.pk}"

            classification = classify_text(text)

            with transaction.atomic():
                product.category_ai_main = classification.main
                product.category_ai_sub = classification.sub
                product.category_ai_conf_main = classification.main_score
                product.category_ai_conf_sub = classification.sub_score
                product.fecha_clasificacion_ai = timezone.now()
                product.save(
                    update_fields=[
                        "category_ai_main",
                        "category_ai_sub",
                        "category_ai_conf_main",
                        "category_ai_conf_sub",
                        "fecha_clasificacion_ai",
                    ]
                )
            
            result_item = {
                "product_id": product.id,
                "main": product.category_ai_main,
                "sub": product.category_ai_sub,
                "conf_main": product.category_ai_conf_main,
                "conf_sub": product.category_ai_conf_sub,
            }
            results.append(result_item)

        except Producto.DoesNotExist:
            logger.warning(f"Producto con ID {product_id} no encontrado.")
        except Exception as e:
            logger.error(f"Error clasificando producto {product_id}: {e}", exc_info=True)
        
        processed_count += 1
        self.update_state(
            state='PROGRESS',
            meta={'current': processed_count, 'total': total_products, 'status': f'Procesado {product.nombre}'}
        )

    logger.info(f"Clasificación completada. {len(results)} productos clasificados.")
    return {'current': total_products, 'total': total_products, 'status': 'Completado!', 'results': results}
