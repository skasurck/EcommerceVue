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

    total = len(collected_urls)
    results = []
    processed_count = 0

    for i, url in enumerate(collected_urls):
        self.update_state(state='PROGRESS', meta={
            'current': i + 1, 'total': total,
            'status': f'Procesando {i + 1}/{total}: {url[:60]}...'
        })
        entry = {'url': url}
        if apply_updates:
            try:
                supplier_product = upsert_product(url)
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
        'results': results,
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
    