from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Producto, Categoria
from .ai import build_text_from_product, classify_text
from django.db import transaction
from django.utils import timezone

logger = get_task_logger(__name__)

# Límite de cuántas de las mejores sugerencias se asignarán al producto.
TOP_N_SUGGESTIONS = 3

@shared_task(bind=True)
def classify_products_task(self, product_ids, overwrite=False):
    """
    Tarea asíncrona de Celery para clasificar productos con múltiples categorías.
    """
    total_products = len(product_ids)
    processed_count = 0
    results = []

    logger.info(f"Iniciando clasificación para {total_products} productos. Sobrescribir: {overwrite}")

    for product_id in product_ids:
        try:
            product = Producto.objects.get(pk=product_id)

            # Lógica de sobrescritura basada en si ya tiene categorías asignadas
            if product.categorias.exists() and not overwrite:
                processed_count += 1
                logger.info(f"Saltando producto {product_id} (ya tiene categorías).")
                self.update_state(
                    state='PROGRESS',
                    meta={'current': processed_count, 'total': total_products, 'status': f'Procesando {product.nombre}'}
                )
                continue
            
            logger.info(f"Clasificando producto {product_id}: {product.nombre}")
            text_to_classify = build_text_from_product(product)
            if not text_to_classify:
                text_to_classify = product.nombre or f"Producto {product.pk}"

            # La función ahora devuelve una lista de sugerencias
            classification_result = classify_text(text_to_classify)
            # Limitar al Top N aquí, en la tarea.
            suggestions = classification_result.suggestions[:TOP_N_SUGGESTIONS]
            logger.info(f"Después de limitar, {len(suggestions)} sugerencias para el producto {product.id}")

            with transaction.atomic():
                # Limpiar la mejor sugerencia anterior
                product.category_ai_main = None
                product.category_ai_sub = None
                product.category_ai_conf_main = None
                product.category_ai_conf_sub = None

                if suggestions:
                    # Guardar la mejor sugerencia en los campos antiguos (opcional, como pidió el usuario)
                    best_suggestion = suggestions[0]
                    try:
                        best_cat_obj = Categoria.objects.get(pk=best_suggestion.id)
                        product.category_ai_main = str(best_cat_obj) # Guardar la ruta completa
                        product.category_ai_conf_main = best_suggestion.score
                    except Categoria.DoesNotExist:
                        logger.warning(f"La mejor categoría sugerida ID {best_suggestion.id} no fue encontrada.")

                    # Asignar todas las categorías sugeridas a la relación ManyToMany
                    suggested_ids = [s.id for s in suggestions]
                    logger.info(f"Asignando IDs de categoría {suggested_ids} al producto {product.id}")
                    product.categorias.set(suggested_ids)
                else:
                    # Si no hay sugerencias, limpiar las categorías existentes si se sobrescribe
                    if overwrite:
                        product.categorias.clear()

                product.fecha_clasificacion_ai = timezone.now()
                product.save()
            
            result_item = {
                "product_id": product.id,
                "assigned_categories": [s.id for s in suggestions]
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
