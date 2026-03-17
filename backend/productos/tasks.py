from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils import timezone

from .ai import ClassificationResult, build_text_from_product, classify_text
from .learning import get_feedback_model, predict_with_feedback
from .models import Producto

logger = get_task_logger(__name__)


@shared_task(bind=True)
def classify_products_task(self, product_ids, overwrite=False):
    """Tarea asincrona de Celery para clasificar productos."""
    total_products = len(product_ids)
    processed_count = 0
    results = []
    feedback_model = get_feedback_model()

    logger.info("Iniciando clasificacion para %s productos. Sobrescribir: %s", total_products, overwrite)
    if feedback_model is not None:
        logger.info(
            "Modelo de aprendizaje por feedback activo (%s muestras).",
            feedback_model.total_samples,
        )
    else:
        logger.info("No hay suficiente feedback manual para entrenamiento; se usara clasificacion base.")

    for product_id in product_ids:
        product_name_for_status = f"Producto {product_id}"
        try:
            product = Producto.objects.get(pk=product_id)
            product_name_for_status = product.nombre or product_name_for_status

            if product.category_ai_main and not overwrite:
                processed_count += 1
                logger.info("Saltando producto %s (ya clasificado).", product_id)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": processed_count,
                        "total": total_products,
                        "status": f"Procesando {product_name_for_status}",
                    },
                )
                continue

            logger.info("Clasificando producto %s: %s", product_id, product_name_for_status)
            text = build_text_from_product(product)
            if not text:
                text = product.nombre or f"Producto {product.pk}"

            feedback_prediction = predict_with_feedback(text, model=feedback_model)
            if feedback_prediction is not None:
                classification = ClassificationResult(
                    main=feedback_prediction.main,
                    sub=feedback_prediction.sub,
                    main_score=feedback_prediction.confidence,
                    sub_score=feedback_prediction.confidence,
                )
            else:
                # Ruta rapida: solo texto para mantener la clasificacion agil.
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

            results.append(
                {
                    "product_id": product.id,
                    "main": product.category_ai_main,
                    "sub": product.category_ai_sub,
                    "conf_main": product.category_ai_conf_main,
                    "conf_sub": product.category_ai_conf_sub,
                }
            )

        except Producto.DoesNotExist:
            logger.warning("Producto con ID %s no encontrado.", product_id)
        except Exception as exc:
            logger.error("Error clasificando producto %s: %s", product_id, exc, exc_info=True)

        processed_count += 1
        self.update_state(
            state="PROGRESS",
            meta={
                "current": processed_count,
                "total": total_products,
                "status": f"Procesado {product_name_for_status}",
            },
        )

    logger.info("Clasificacion completada. %s productos clasificados.", len(results))
    return {
        "current": total_products,
        "total": total_products,
        "status": "Completado!",
        "results": results,
    }
