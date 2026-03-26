# suppliers/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from suppliers.models import SupplierProduct, ProductSupplierMap
from productos.models import Producto
from suppliers.utils import effective_qty
from decimal import Decimal

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_supermex_scraper(self, start_url=None, product_urls=None, limit=0,
                         max_pages=None, sleep_s=None, apply_updates=True, http2=True):
    from suppliers.management.commands.sync_supermex import create_or_update_producto_from_supplier
    from suppliers.scraper_supermex import get_client, plp_collect_all, upsert_product

    self.update_state(state='PROGRESS', meta={'current': 0, 'total': 0, 'status': 'Recolectando URLs...'})

    try:
        if product_urls:
            collected_urls = product_urls[:limit or None]
        else:
            with get_client(http2=http2) as client:
                collected_urls = plp_collect_all(
                    client, start_url, limit=limit,
                    sleep_s=sleep_s, max_pages=max_pages,
                )
    except Exception as exc:
        logger.exception("Error recolectando URLs: %s", exc)
        raise

    # Invertir orden: procesar primero los más viejos (última página) para que
    # los más nuevos de Supermex queden con fecha_creacion más reciente en el DB
    collected_urls = list(reversed(collected_urls))

    # Pre-cargar URLs ya existentes para saltarlas rápidamente
    existing_urls = set(
        SupplierProduct.objects.filter(supplier='supermex').values_list('product_url', flat=True)
    )

    total = len(collected_urls)
    results = []
    processed_count = 0
    skipped_count = 0

    for i, url in enumerate(collected_urls):
        self.update_state(state='PROGRESS', meta={
            'current': i + 1, 'total': total,
            'status': f'Procesando {i + 1}/{total}: {url[:60]}...'
        })
        entry = {'url': url}

        # Saltar si el producto ya existe en la base de datos
        if url in existing_urls:
            entry['status'] = 'exists'
            skipped_count += 1
            results.append(entry)
            continue

        if apply_updates:
            try:
                supplier_product = upsert_product(url)
                existing_urls.add(url)  # evita duplicados dentro de la misma ejecución
                pre_existing = Producto.objects.filter(sku=supplier_product.supplier_sku).exists()
                django_product = create_or_update_producto_from_supplier(supplier_product)
                entry['status'] = 'ok'
                if django_product:
                    entry['django_product'] = {
                        'id': django_product.id,
                        'sku': django_product.sku,
                        'nombre': django_product.nombre,
                        'action': 'created' if not pre_existing else 'updated',
                    }
                processed_count += 1
            except Exception as exc:
                logger.exception("Error importando %s: %s", url, exc)
                entry['status'] = 'error'
                entry['error'] = str(exc)
        else:
            entry['status'] = 'skipped'
        results.append(entry)

    return {
        'current': total, 'total': total,
        'status': 'Completado',
        'collected_count': total,
        'processed_count': processed_count,
        'skipped_existing': skipped_count,
        'results': results,
    }

@shared_task(bind=True)
def run_supermex_stock_sync(self, http2: bool = True, sleep_s: float = 0.3):
    """
    Scraper ligero: solo actualiza precio + stock de productos ya existentes.
    No toca nombre/descripción/imágenes ni crea productos nuevos.
    Ideal para ejecución diaria.
    """
    from suppliers.scraper_supermex import get_client, sync_stock_for_product
    from suppliers.models import SupplierProduct

    products = list(SupplierProduct.objects.filter(supplier="supermex").values_list("id", flat=True))
    total = len(products)
    updated = 0
    errors = 0

    self.update_state(state="PROGRESS", meta={"current": 0, "total": total, "status": f"Iniciando sync de {total} productos..."})

    with get_client(http2=http2) as client:
        for i, sp_id in enumerate(products):
            try:
                sp = SupplierProduct.objects.get(pk=sp_id)
                self.update_state(state="PROGRESS", meta={
                    "current": i + 1, "total": total,
                    "status": f"{i + 1}/{total}: {sp.name[:50]}",
                })
                result = sync_stock_for_product(sp, client)

                update_fields = ["in_stock", "available_qty", "last_seen"]
                sp.in_stock = result["in_stock"]
                sp.available_qty = result["qty"]
                if result["price"] is not None:
                    sp.price_supplier = result["price"]
                    update_fields.append("price_supplier")
                sp.save(update_fields=update_fields)
                updated += 1
            except Exception as exc:
                logger.warning("Error sync stock %s: %s", sp_id, exc)
                errors += 1

            if sleep_s > 0:
                import time
                time.sleep(sleep_s)

    apply_rules()

    return {
        "current": total, "total": total,
        "status": "Completado",
        "updated": updated,
        "errors": errors,
    }


MARKUP = Decimal("1.15")  # tu +15%

def apply_rules():
    links = ProductSupplierMap.objects.select_related("product").all()
    for link in links:
        p: Producto = link.product
        try:
            sp = SupplierProduct.objects.get(supplier_sku=link.supplier_sku)
        except SupplierProduct.DoesNotExist:
            continue

        qty_eff = effective_qty(sp.available_qty, sp.in_stock)

        # 1) Stock / estado inventario / visibilidad
        if qty_eff > 0:
            # En existencia
            p.estado_inventario = "en_existencia"
            p.disponible = True
            p.visibilidad = True
            # solo sube stock si lo tienes en 0 o menor que el mínimo virtual (evita inflar si ya tienes real)
            if p.stock == 0 or p.stock < qty_eff:
                p.stock = qty_eff
        else:
            # Agotado
            p.estado_inventario = "agotado"
            # Si quisieras ocultar al quedar agotado:
            if getattr(link, "auto_hide_when_oos", True):
                p.visibilidad = False
            p.disponible = False
            # opcional: no toques p.stock para conservar histórico

        # 2) Precios (aplicar +15% sobre price_supplier, si viene > 0)
        if sp.price_supplier and sp.price_supplier > 0:
            base = sp.price_supplier
            precio_nuevo = (base * MARKUP).quantize(Decimal("0.01"))
            p.precio_normal = precio_nuevo
            # si manejas rebajado aparte, decide tu lógica aquí

        p.save(update_fields=[
            "estado_inventario", "disponible", "visibilidad",
            "stock", "precio_normal"
        ])
    