import os
import re
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils import timezone

from .ai import ClassificationResult, build_text_from_product, classify_text
from .learning import get_feedback_model, predict_with_feedback
from .models import Categoria, Producto

logger = get_task_logger(__name__)


@shared_task(bind=True, name='productos.generate_keywords', max_retries=2, default_retry_delay=60)
def generate_keywords_task(self, product_id):
    """
    Genera palabras clave de búsqueda automáticamente con Claude Haiku.
    Se ejecuta en background al guardar un producto nuevo o editado.
    """
    try:
        product = Producto.objects.get(pk=product_id)
    except Producto.DoesNotExist:
        logger.warning("generate_keywords_task: producto %s no encontrado.", product_id)
        return

    # Construir texto de entrada
    parts = [p for p in [product.nombre, product.descripcion_corta, product.sku] if p]
    text = ' | '.join(parts).strip()
    if not text:
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("generate_keywords_task: OPENAI_API_KEY no configurada.")
        return

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = (
            "Eres un experto en búsqueda de productos de tecnología y cómputo en México.\n"
            "Para el siguiente producto, genera una lista de palabras clave en ESPAÑOL que un cliente "
            "podría escribir en un buscador para encontrarlo.\n"
            "Incluye: sinónimos comunes, abreviaciones (cpu, gpu, ram, hdd, ssd...), términos alternativos "
            "en lenguaje coloquial, características técnicas relevantes, y traducciones al español de términos en inglés.\n"
            "NO repitas palabras que ya están en el nombre del producto.\n"
            "Devuelve SOLO las palabras/frases cortas separadas por espacios, sin puntuación ni explicaciones.\n\n"
            f"Producto: {text[:300]}\n\n"
            "Keywords:"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=150,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.choices[0].message.content.strip().lower()
        # Limpiar: solo letras, números, espacios y algunos caracteres especiales
        clean = re.sub(r'[^\w\s]', ' ', raw, flags=re.UNICODE)
        clean = re.sub(r'\s+', ' ', clean).strip()

        Producto.objects.filter(pk=product_id).update(search_keywords=clean)
        logger.info(
            "Keywords generadas para producto %s (%s): %s",
            product_id, product.nombre[:40], clean[:120]
        )

    except Exception as exc:
        logger.error("Error generando keywords para producto %s: %s", product_id, exc)
        raise self.retry(exc=exc)

# Confianza mínima (0-1) para auto-aplicar sin revisión manual.
# Umbral de confianza para auto-aprobar sin revisión manual.
# GPT retorna siempre 0.90 fijo; con match_type="best_effort" queda en revisión.
AUTO_APPROVE_THRESHOLD = 0.60


def _find_category_by_path(path: str) -> Categoria | None:
    """
    Busca una categoría existente por ruta 'Main > Sub > Hoja'.
    No crea categorías nuevas — solo busca en las existentes.
    """
    if not path:
        return None
    parts = [seg.strip() for seg in path.split(">") if seg.strip()]
    if not parts:
        return None

    current_parent = None
    last_category = None
    for part in parts:
        category = Categoria.objects.filter(nombre=part, parent=current_parent).first()
        if not category:
            return None
        current_parent = category
        last_category = category
    return last_category


@shared_task(bind=True, name='productos.recalcular_destacados')
def recalcular_destacados_task(self):
    """
    Tarea periódica que recalcula los productos destacados automáticos.
    Programada para ejecutarse cada hora desde celery.py.
    """
    from .services import actualizar_destacados_automaticos
    logger.info("Iniciando recálculo de productos destacados automáticos...")
    try:
        actualizar_destacados_automaticos()
        logger.info("Recálculo de destacados completado.")
        return {'status': 'ok'}
    except Exception as exc:
        logger.exception("Error en recálculo de destacados: %s", exc)
        raise


@shared_task(bind=True)
def classify_products_task(self, product_ids, overwrite=False):
    """Tarea asincrona de Celery para clasificar productos."""
    total_products = len(product_ids)
    processed_count = 0
    auto_applied = 0
    pending_review = 0
    feedback_model = get_feedback_model()

    logger.info("Iniciando clasificacion para %s productos. Sobrescribir: %s", total_products, overwrite)

    for product_id in product_ids:
        product_name_for_status = f"Producto {product_id}"
        try:
            product = Producto.objects.get(pk=product_id)
            product_name_for_status = product.nombre or product_name_for_status

            if product.category_ai_main and not overwrite:
                processed_count += 1
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": processed_count,
                        "total": total_products,
                        "auto_applied": auto_applied,
                        "pending_review": pending_review,
                        "status": f"Saltando {product_name_for_status} (ya clasificado)",
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
                classification = classify_text(text)

            confidence = classification.main_score or 0.0
            full_path = classification.sub or classification.main

            # Alta confianza → auto-aplicar la categoría directamente
            if confidence >= AUTO_APPROVE_THRESHOLD and full_path:
                category = _find_category_by_path(full_path)
                if category is None and classification.main:
                    category = _find_category_by_path(classification.main)

                if category:
                    with transaction.atomic():
                        product.categorias.set([category])
                        product.category_ai_main = None
                        product.category_ai_sub = None
                        product.category_ai_leaf = None
                        product.category_ai_match_type = None
                        product.category_ai_conf_main = None
                        product.category_ai_conf_sub = None
                        product.fecha_clasificacion_ai = timezone.now()
                        product.save(update_fields=[
                            "category_ai_main", "category_ai_sub",
                            "category_ai_leaf", "category_ai_match_type",
                            "category_ai_conf_main", "category_ai_conf_sub",
                            "fecha_clasificacion_ai",
                        ])
                    auto_applied += 1
                    logger.info(
                        "Auto-aplicado producto %s → '%s' (confianza %.0f%%)",
                        product_id, full_path, confidence * 100,
                    )
                else:
                    # Categoría no encontrada en DB → dejar para revisión
                    logger.warning(
                        "Producto %s: categoría '%s' no existe en BD, enviando a revisión.",
                        product_id, full_path,
                    )
                    with transaction.atomic():
                        product.category_ai_main = classification.main
                        product.category_ai_sub = classification.sub
                        product.category_ai_leaf = classification.leaf
                        product.category_ai_match_type = classification.match_type
                        product.category_ai_conf_main = confidence
                        product.category_ai_conf_sub = classification.sub_score
                        product.fecha_clasificacion_ai = timezone.now()
                        product.save(update_fields=[
                            "category_ai_main", "category_ai_sub",
                            "category_ai_leaf", "category_ai_match_type",
                            "category_ai_conf_main", "category_ai_conf_sub",
                            "fecha_clasificacion_ai",
                        ])
                    pending_review += 1
            else:
                # Confianza baja → guardar sugerencia para revisión manual
                with transaction.atomic():
                    product.category_ai_main = classification.main
                    product.category_ai_sub = classification.sub
                    product.category_ai_leaf = classification.leaf
                    product.category_ai_match_type = classification.match_type
                    product.category_ai_conf_main = confidence
                    product.category_ai_conf_sub = classification.sub_score
                    product.fecha_clasificacion_ai = timezone.now()
                    product.save(update_fields=[
                        "category_ai_main", "category_ai_sub",
                        "category_ai_leaf", "category_ai_match_type",
                        "category_ai_conf_main", "category_ai_conf_sub",
                        "fecha_clasificacion_ai",
                    ])
                pending_review += 1
                logger.info(
                    "Producto %s requiere revisión (confianza %.0f%%): %s",
                    product_id, confidence * 100, full_path,
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
                "auto_applied": auto_applied,
                "pending_review": pending_review,
                "status": f"Procesado {product_name_for_status}",
            },
        )

        # Pausa para evitar rate limiting de la API
        if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
            time.sleep(0.5)

    logger.info(
        "Clasificacion completada. Auto-aplicados: %s | Pendientes de revisión: %s",
        auto_applied, pending_review,
    )
    return {
        "current": total_products,
        "total": total_products,
        "auto_applied": auto_applied,
        "pending_review": pending_review,
        "status": "Completado!",
    }
