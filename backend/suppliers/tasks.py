# suppliers/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from suppliers.models import SupplierProduct, ProductSupplierMap, SupplierStockHistory
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

    # Saltar solo si el producto existe en SupplierProduct Y tiene un Producto Django creado
    existing_skus = set(Producto.objects.values_list('sku', flat=True))
    existing_urls = set(
        SupplierProduct.objects.filter(supplier='supermex', supplier_sku__in=existing_skus)
        .values_list('product_url', flat=True)
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
def run_supermex_stock_sync(self, http2: bool = True, sleep_s: float = 0.3, sync_log_id: int = None):
    """
    Scraper ligero: solo actualiza precio + stock de productos ya existentes.
    No toca nombre/descripción/imágenes ni crea productos nuevos.
    Ideal para ejecución diaria.
    """
    from suppliers.scraper_supermex import get_client, sync_stock_for_product
    from suppliers.models import SupplierProduct, SupplierSyncLog, SupplierSyncLogEntry
    import time

    # Crear o reutilizar el registro de log
    if sync_log_id:
        sync_log = SupplierSyncLog.objects.get(pk=sync_log_id)
    else:
        sync_log = SupplierSyncLog.objects.create(tipo="stock_sync", estado="running")

    products = list(SupplierProduct.objects.filter(supplier="supermex", is_active=True).values_list("id", flat=True))
    total = len(products)
    updated = 0
    unchanged = 0
    errors = 0
    deactivated = 0

    sync_log.total = total
    sync_log.save(update_fields=["total"])

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

                # --- 404: incrementar contador y desactivar si supera el límite ---
                if result.get("method") == "404":
                    sp.consecutive_404s = (sp.consecutive_404s or 0) + 1
                    sp.in_stock = False
                    sp.available_qty = 0
                    sp.last_seen = timezone.now()
                    save_fields = ["consecutive_404s", "in_stock", "available_qty", "last_seen"]
                    if sp.consecutive_404s >= 3:
                        sp.is_active = False
                        save_fields.append("is_active")
                        deactivated += 1
                        logger.warning("Desactivado %s tras %d 404s consecutivos", sp.supplier_sku, sp.consecutive_404s)
                    sp.save(update_fields=save_fields)
                    updated += 1
                    continue

                # --- Respuesta normal: resetear contador 404 si venía con fallos ---
                prev_qty = sp.available_qty
                prev_price = sp.price_supplier
                prev_in_stock = sp.in_stock
                update_fields = ["last_seen"]
                if sp.consecutive_404s > 0:
                    sp.consecutive_404s = 0
                    update_fields.append("consecutive_404s")
                if result["in_stock"] != sp.in_stock:
                    sp.in_stock = result["in_stock"]
                    update_fields.append("in_stock")
                if result["qty"] != sp.available_qty:
                    sp.available_qty = result["qty"]
                    update_fields.append("available_qty")
                if result["price"] is not None and result["price"] != sp.price_supplier:
                    sp.price_supplier = result["price"]
                    update_fields.append("price_supplier")
                sp.last_seen = timezone.now()
                sp.save(update_fields=update_fields)

                # Guardar snapshot de stock si el qty cambió (para estadísticas de ventas)
                if "available_qty" in update_fields:
                    SupplierStockHistory.objects.create(
                        supplier_product=sp,
                        available_qty=result["qty"],
                        in_stock=result["in_stock"],
                    )

                if len(update_fields) > 1:
                    updated += 1
                    logger.info("Actualizado %s: %s (qty %s→%s)", sp.supplier_sku, update_fields, prev_qty, result["qty"])
                    # Guardar detalle de cambios en el log
                    if "available_qty" in update_fields:
                        SupplierSyncLogEntry.objects.create(
                            sync_log=sync_log, tipo="cambio",
                            supplier_sku=sp.supplier_sku, name=sp.name, url=sp.product_url,
                            campo="stock", valor_anterior=str(prev_qty), valor_nuevo=str(result["qty"]),
                        )
                    if "price_supplier" in update_fields:
                        SupplierSyncLogEntry.objects.create(
                            sync_log=sync_log, tipo="cambio",
                            supplier_sku=sp.supplier_sku, name=sp.name, url=sp.product_url,
                            campo="precio", valor_anterior=str(prev_price), valor_nuevo=str(result["price"]),
                        )
                    if "in_stock" in update_fields:
                        SupplierSyncLogEntry.objects.create(
                            sync_log=sync_log, tipo="cambio",
                            supplier_sku=sp.supplier_sku, name=sp.name, url=sp.product_url,
                            campo="disponibilidad",
                            valor_anterior="En stock" if prev_in_stock else "Agotado",
                            valor_nuevo="En stock" if result["in_stock"] else "Agotado",
                        )
                else:
                    unchanged += 1
                    logger.debug("Sin cambios %s", sp.supplier_sku)
            except Exception as exc:
                logger.warning("Error sync stock %s: %s", sp_id, exc)
                errors += 1
                try:
                    sp_obj = SupplierProduct.objects.get(pk=sp_id)
                    SupplierSyncLogEntry.objects.create(
                        sync_log=sync_log, tipo="error",
                        supplier_sku=sp_obj.supplier_sku, name=sp_obj.name, url=sp_obj.product_url,
                        mensaje_error=str(exc),
                    )
                except Exception:
                    SupplierSyncLogEntry.objects.create(
                        sync_log=sync_log, tipo="error",
                        supplier_sku=str(sp_id), mensaje_error=str(exc),
                    )

            if sleep_s > 0:
                time.sleep(sleep_s)

    apply_rules()

    sync_log.estado = "completed"
    sync_log.fecha_fin = timezone.now()
    sync_log.updated = updated
    sync_log.unchanged = unchanged
    sync_log.errors = errors
    sync_log.deactivated = deactivated
    sync_log.save(update_fields=["estado", "fecha_fin", "updated", "unchanged", "errors", "deactivated"])

    return {
        "current": total, "total": total,
        "status": "Completado",
        "updated": updated,
        "unchanged": unchanged,
        "errors": errors,
        "deactivated": deactivated,
        "sync_log_id": sync_log.id,
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

        changed_fields = []

        # 1) Stock / estado inventario / visibilidad
        if qty_eff > 0:
            new_estado = "en_existencia"
            new_disponible = True
            new_visibilidad = True
            new_stock = qty_eff
        else:
            new_estado = "agotado"
            new_disponible = False
            new_visibilidad = False if getattr(link, "auto_hide_when_oos", True) else p.visibilidad
            new_stock = p.stock  # conservar histórico

        if p.estado_inventario != new_estado:
            p.estado_inventario = new_estado
            changed_fields.append("estado_inventario")
        if p.disponible != new_disponible:
            p.disponible = new_disponible
            changed_fields.append("disponible")
        if p.visibilidad != new_visibilidad:
            p.visibilidad = new_visibilidad
            changed_fields.append("visibilidad")
        if p.stock != new_stock:
            p.stock = new_stock
            changed_fields.append("stock")

        # 2) Precios (aplicar +15% sobre price_supplier, si viene > 0 y es razonable)
        if sp.price_supplier and 0 < sp.price_supplier <= Decimal("500000"):
            precio_nuevo = (sp.price_supplier * MARKUP).quantize(Decimal("0.01"))
            if precio_nuevo < Decimal("99999999.99") and p.precio_normal != precio_nuevo:
                p.precio_normal = precio_nuevo
                changed_fields.append("precio_normal")

        if changed_fields:
            p.save(update_fields=changed_fields)


@shared_task(name="suppliers.tasks.sync_supermex_full")
def sync_supermex_full():
    """
    Tarea diaria a las 3 AM: actualiza stock y precios.
    Cada 3 días (día del año divisible entre 3) también importa productos nuevos.
    """
    from suppliers.models import SupplierSyncLog
    import datetime

    hoy = datetime.date.today()
    importar_nuevos = (hoy.timetuple().tm_yday % 3 == 0)

    if importar_nuevos:
        # Crear un log unificado para stock + importación
        sync_log = SupplierSyncLog.objects.create(tipo="stock_then_import", estado="running")
        # Primero sync de stock
        run_supermex_stock_sync.apply(kwargs={"http2": True, "sleep_s": 0.3, "sync_log_id": sync_log.id}).get()
        # Luego importar productos nuevos
        _run_import_and_log(sync_log)
    else:
        run_supermex_stock_sync.apply(kwargs={"http2": True, "sleep_s": 0.3}).get()


def _run_import_and_log(sync_log):
    """Ejecuta la importación de productos nuevos y guarda el resultado en sync_log."""
    from suppliers.models import SupplierSyncLog, SupplierSyncLogEntry
    from suppliers.scraper_supermex import get_client, plp_collect_all, upsert_product
    from suppliers.management.commands.sync_supermex import create_or_update_producto_from_supplier
    from productos.models import Producto

    CATEGORIES = [
        "https://www.supermexdigital.mx/shop/monitores",
        "https://www.supermexdigital.mx/shop/almacenamiento",
    ]

    existing_skus = set(Producto.objects.values_list('sku', flat=True))
    from suppliers.models import SupplierProduct
    existing_urls = set(
        SupplierProduct.objects.filter(supplier='supermex', supplier_sku__in=existing_skus)
        .values_list('product_url', flat=True)
    )

    collected_urls = []
    with get_client(http2=True) as client:
        for cat in CATEGORIES:
            try:
                urls = plp_collect_all(client, cat, sleep_s=0.6, max_pages=5)
                collected_urls.extend(urls)
            except Exception as exc:
                logger.warning("Error recolectando categoría %s: %s", cat, exc)

    new_imported = 0
    skipped = 0
    import time

    with get_client(http2=True) as client:
        for url in collected_urls:
            if url in existing_urls:
                skipped += 1
                continue
            try:
                supplier_product = upsert_product(url)
                existing_urls.add(url)
                create_or_update_producto_from_supplier(supplier_product)
                new_imported += 1
                SupplierSyncLogEntry.objects.create(
                    sync_log=sync_log, tipo="cambio",
                    supplier_sku=supplier_product.supplier_sku,
                    name=supplier_product.name,
                    url=url,
                    campo="importacion",
                    valor_anterior="",
                    valor_nuevo="nuevo",
                )
            except Exception as exc:
                logger.warning("Error importando %s: %s", url, exc)
                SupplierSyncLogEntry.objects.create(
                    sync_log=sync_log, tipo="error",
                    url=url, mensaje_error=str(exc),
                )
            time.sleep(0.6)

    sync_log.new_imported = new_imported
    sync_log.skipped_existing = skipped
    sync_log.estado = "completed"
    sync_log.fecha_fin = timezone.now()
    sync_log.save(update_fields=["new_imported", "skipped_existing", "estado", "fecha_fin"])


@shared_task(name="suppliers.tasks.recheck_inactive_products")
def recheck_inactive_products():
    """
    Revisión semanal de productos desactivados por 404.
    Si el producto vuelve a responder con 200, lo reactiva automáticamente.
    """
    from suppliers.scraper_supermex import get_client, sync_stock_for_product

    inactive = list(
        SupplierProduct.objects.filter(supplier="supermex", is_active=False)
        .values_list("id", flat=True)
    )
    total = len(inactive)
    reactivated = 0
    still_dead = 0

    logger.info("[RECHECK] Revisando %d productos inactivos...", total)

    with get_client(http2=True) as client:
        for sp_id in inactive:
            import time
            try:
                sp = SupplierProduct.objects.get(pk=sp_id)
                result = sync_stock_for_product(sp, client)

                if result.get("method") == "404":
                    still_dead += 1
                    logger.debug("[RECHECK] Sigue inactivo: %s", sp.supplier_sku)
                else:
                    # Volvió a responder — reactivar
                    sp.is_active = True
                    sp.consecutive_404s = 0
                    sp.in_stock = result["in_stock"]
                    sp.available_qty = result["qty"]
                    sp.last_seen = timezone.now()
                    save_fields = ["is_active", "consecutive_404s", "in_stock", "available_qty", "last_seen"]
                    if result["price"] is not None:
                        sp.price_supplier = result["price"]
                        save_fields.append("price_supplier")
                    sp.save(update_fields=save_fields)
                    reactivated += 1
                    logger.info("[RECHECK] Reactivado: %s", sp.supplier_sku)

            except Exception as exc:
                logger.warning("[RECHECK] Error en %s: %s", sp_id, exc)

            time.sleep(0.5)

    logger.info("[RECHECK] Completado: %d reactivados, %d siguen sin responder de %d revisados", reactivated, still_dead, total)
    return {"total": total, "reactivated": reactivated, "still_dead": still_dead}
