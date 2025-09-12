# suppliers/management/commands/sync_supermex.py
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import OperationalError, close_old_connections, connection
from decimal import Decimal, ROUND_HALF_UP
import time
from suppliers.scraper_supermex import (
    get_client, get_with, parse_plp, plp_collect_all, upsert_product
)
from suppliers.models import SupplierProduct, ProductSupplierMap
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import httpx, os
from productos.models import Producto
from suppliers.pricing import apply_markup as pricing_apply_markup
from django.db.models import ForeignKey
from django.utils.text import slugify
from uuid import uuid4



MIN_VIRTUAL = getattr(settings, "SUPPLIER_MIN_VIRTUAL_QTY", 1)


def _db_retry(op, *args, retries: int = 5, base_delay: float = 0.5, **kwargs):
    for attempt in range(retries):
        try:
            return op(*args, **kwargs)
        except OperationalError as exc:
            if "database is locked" in str(exc).lower() and attempt < retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                close_old_connections()
                continue
            raise


def retry_save(obj, **kwargs):
    return _db_retry(obj.save, **kwargs)


def retry_get_or_create(manager, **kwargs):
    return _db_retry(manager.get_or_create, **kwargs)


def retry_create(manager, **kwargs):
    return _db_retry(manager.create, **kwargs)


def _download_first_image(sp: SupplierProduct):
    if not sp.image_urls:
        return None
    url = sp.image_urls[0]
    fn = os.path.basename(urlparse(url).path) or "img.jpg"
    with httpx.Client(follow_redirects=True, timeout=30) as c:
        for attempt in range(3):
            try:
                r = c.get(url)
                r.raise_for_status()
                return fn, r.content
            except httpx.HTTPError:
                if attempt == 2:
                    raise
                time.sleep(1 * (2 ** attempt))

def create_or_update_producto_from_supplier(sp: SupplierProduct) -> Producto | None:
    if sp.price_supplier is None:
        print(
            f"[WARN] SupplierProduct {sp.supplier_sku} sin precio; se omite creación/actualización de Producto"
        )
        return None

    # precio con markup (ej. +15%)
    price_sale = pricing_apply_markup(Decimal(sp.price_supplier))

    prod, created = retry_get_or_create(
        Producto.objects,
        sku=sp.supplier_sku,
        defaults={
            "nombre": sp.name[:100],
            "descripcion_corta": "",
            "descripcion_larga": sp.description_html or "",
            "precio_normal": price_sale,
            "precio_rebajado": None,
            "visibilidad": False,              # entra como borrador
            "estado": "borrador",
            "stock": max(sp.available_qty or 0, MIN_VIRTUAL) if sp.in_stock else 0,
            "estado_inventario": "en_existencia" if sp.in_stock else "agotado",
        },
    )

    # si ya existía, actualiza precio/stock/desc
    if not created:
        prod.precio_normal = price_sale
        prod.descripcion_larga = sp.description_html or prod.descripcion_larga
        prod.stock = max(sp.available_qty or 0, MIN_VIRTUAL) if sp.in_stock else 0
        prod.estado_inventario = "en_existencia" if prod.stock > 0 else "agotado"
        retry_save(prod)

    # imagen principal (solo si no tiene)
    if created and not prod.imagen_principal:
        try:
            got = _download_first_image(sp)
            if got:
                fn, content = got
                _db_retry(prod.imagen_principal.save, fn, ContentFile(content), save=True)
        except Exception:
            pass

    # vincula mapa proveedor↔producto
    retry_get_or_create(
        ProductSupplierMap.objects,
        product=prod,
        supplier="supermex",
        supplier_sku=sp.supplier_sku,
        defaults={"auto_hide_when_oos": True},
    )

    # === CATEGORÍAS + GALERÍA ===
    try:
        # Traemos el HTML de la PDP una sola vez para leer breadcrumb
        with httpx.Client(follow_redirects=True, timeout=30) as c:
            r = c.get(sp.product_url)
            r.raise_for_status()
            html = r.text
        cats = _extract_categories_from_html(html)
        if cats:
            _ensure_categories(prod, cats)
    except Exception:
        pass

    # Guarda las imágenes adicionales en galería
    try:
        _ensure_gallery(prod, sp)
    except Exception:
        pass

    return prod
# ------- Config por defecto (puedes mover esto a settings.py si prefieres) -------
DEFAULT_CATEGORIES = [
    "https://www.supermexdigital.mx/shop/computadoras",
    "https://www.supermexdigital.mx/shop/monitores",
    "https://www.supermexdigital.mx/shop/almacenamiento",
]
# ---------------------------------------------------------------------------------
max_pages=15
def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def apply_markup_pct(price_supplier: Decimal, pct: Decimal) -> Decimal:
    return quantize_money(price_supplier * (Decimal("1.00") + pct))

def _extract_categories_from_html(html: str) -> list[str]:
        """Lee el breadcrumb de la PDP y devuelve nombres de categorías (texto visible)."""
        from selectolax.parser import HTMLParser
        t = HTMLParser(html)
        names = []
        # Breadcrumb típico de Odoo: .o_wsale_breadcrumb a[href*="/shop/category/"]
        for a in t.css(".o_wsale_breadcrumb a[href*='/shop/category/']"):
            txt = a.text(strip=True)
            if txt and txt.lower() not in {"all products", "todos los productos", "todo", "productos"}:
                names.append(txt)
        return names

def _ensure_categories(producto, category_names: list[str]):
    """
    Construye la jerarquía a partir del breadcrumb: [Computadoras, Componentes, ...]
    - Crea/ajusta padre->hijo si el modelo tiene FK a sí mismo ('padre' o 'parent').
    - Añade TODAS las categorías al M2M 'categorias'.
    - Asigna como 'categoria' principal la última (hoja) si el campo está vacío.
    """
    from productos.models import Categoria

    # Detecta si hay FK self ('padre' o 'parent')
    parent_field_name = None
    for f in Categoria._meta.get_fields():
        if isinstance(f, ForeignKey) and getattr(f.remote_field, 'model', None) is Categoria:
            if f.name in ("padre", "parent"):
                parent_field_name = f.name
                break

    parent = None
    last_cat = None

    for name in category_names:
        name_clean = (name or "").strip()
        if not name_clean:
            continue

        slug = slugify(name_clean)[:50] or f"cat-{uuid4().hex[:8]}"
        defaults = {"nombre": name_clean[:100]}

        if parent_field_name:
            cat, created = retry_get_or_create(
                Categoria.objects,
                slug=slug,
                defaults={**defaults, parent_field_name: parent},
            )
            # si existía y el padre no coincide, corrígelo
            if not created:
                current_parent = getattr(cat, parent_field_name)
                want_id = parent.id if parent else None
                has_id = current_parent.id if current_parent else None
                if has_id != want_id:
                    setattr(cat, parent_field_name, parent)
                    retry_save(cat, update_fields=[parent_field_name])
        else:
            cat, _ = retry_get_or_create(
                Categoria.objects,
                slug=slug,
                defaults=defaults,
            )

        _db_retry(producto.categorias.add, cat)
        parent = cat
        last_cat = cat

    if last_cat and not producto.categoria_id:
        producto.categoria = last_cat
        retry_save(producto, update_fields=["categoria"])
  

def _ensure_gallery(producto, sp, max_images: int = 12):
    """
    Descarga y guarda TODAS las imágenes 2..n en ImagenProducto.
    - Evita duplicar por URL (limpiando query params).
    - Genera nombres de archivo únicos para que no se pisen.
    - Respeta un máximo (por defecto 12) para no desbordar.
    """
    from productos.models import ImagenProducto
    from urllib.parse import urlsplit, urlunsplit

    if not sp.image_urls:
        return

    # 0 es la principal; galería empieza en 1
    raw_urls = sp.image_urls[1:]
    if not raw_urls:
        return

    def _clean(u: str) -> str:
        p = urlsplit(u)
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

    # URLs limpias para evitar repes (p.ej. ?unique=...)
    clean_urls = []
    seen = set()
    for u in raw_urls:
        cu = _clean(u)
        if cu not in seen:
            seen.add(cu)
            clean_urls.append((u, cu))

    # Evita repetir si ya está en galería (guardamos huellas por filename parcial en DB,
    # pero lo robusto es recordar qué URLs ya subimos; si tu modelo no tiene campo URL, usamos set local)
    existing_names = set(
        ImagenProducto.objects.filter(producto=producto).values_list("imagen", flat=True)
    )

    added = 0
    with httpx.Client(follow_redirects=True, timeout=30) as c:
        for idx, (orig, clean) in enumerate(clean_urls, start=1):
            if added >= max_images:
                break
            # nombre único siempre (evita colisiones)
            ext = os.path.splitext(urlparse(clean).path)[1].lower() or ".jpg"
            fn = f"{producto.pk}_{idx}_{uuid4().hex}{ext}"

            if any(fn in str(p) for p in existing_names):
                fn = f"{producto.pk}_{idx}_{uuid4().hex}{ext}"

            success = False
            for attempt in range(3):
                try:
                    r = c.get(orig)
                    r.raise_for_status()
                    img_content = ContentFile(r.content, name=fn)
                    retry_create(ImagenProducto.objects, producto=producto, imagen=img_content)
                    existing_names.add(f"productos/galeria/{fn}")
                    added += 1
                    success = True
                    break
                except httpx.HTTPError:
                    if attempt == 2:
                        break
                    time.sleep(1 * (2 ** attempt))
                except Exception:
                    if attempt == 2:
                        break
                    time.sleep(1 * (2 ** attempt))
            if not success:
                continue
  


class Command(BaseCommand):
    help = "Sincroniza productos desde Supermex: crea/actualiza SupplierProduct, mapea por SKU con Producto y actualiza precio/stock."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            help="Sincroniza una sola URL de producto de Supermex (PDP)."
        )
        parser.add_argument(
            "--category",
            action="append",
            help="Agrega una URL de categoría (PLP) para rastrear múltiples productos. Se puede pasar varias veces."
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Rastrea todas las categorías por defecto (lista embebida)."
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Límite de productos a procesar por ejecución (0 = sin límite)."
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=1.0,
            help="Sleep (segundos) entre requests para rate limiting."
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No guarda cambios en Producto / Map; solo muestra lo que haría."
        )
        parser.add_argument(
            "--markup",
            type=float,
            default=15.0,
            help="Porcentaje de markup a aplicar sobre el precio del proveedor. Default 15.0"
        )
        parser.add_argument(
            "--pdp",
            action="append",
            help="URL de PDP (repetible). Puedes pasar varias --pdp."
        )

    def handle(self, *args, **opts):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=8000;")

        url = opts.get("url")
        cats = opts.get("category") or []
        do_all = opts.get("all")
        limit = int(opts.get("limit") or 0)
        sleep_s = float(opts.get("sleep") or 1.0)
        dry = bool(opts.get("dry_run"))
        markup_pct = Decimal(str(opts.get("markup") or 15.0)) / Decimal("100")
        self.created_count = 0
        self.updated_count = 0
        processed = 0
        # --------- IMPORTANTE: declara pdp_urls ANTES de usarla ----------
        pdp_urls: list[str] = []
        # ---------------------------------------------------------------

        # Mínimo virtual (si no lo tienes en settings, por defecto 2)
        min_virtual = getattr(settings, "SUPPLIER_MIN_VIRTUAL_QTY", 1)

        if not opts.get("url") and not opts.get("category") and not opts.get("all") and not opts.get("pdp"):
            self.stdout.write(self.style.WARNING(
                "No pasaste --url / --category / --all / --pdp. Actualizaré únicamente los SupplierProduct existentes."
            ))

        # --- separar --pdp en PDPs y categorías ---
        pdp_in = opts.get("pdp") or []
        cat_like, pdp_like = [], []
        for u in pdp_in:
            (cat_like if "/shop/category/" in u else pdp_like).append(u)
        pdp_urls.extend(pdp_like)

        # --- rastrear categorías que vinieron por --pdp ---
        if cat_like:
            with get_client() as client:
                for c_url in cat_like:
                    self.stdout.write(f"[CATEG] (desde --pdp) Rastreo: {c_url}")
                    hrefs = plp_collect_all(client, c_url, limit=limit, sleep_s=sleep_s)
                    pdp_urls.extend(hrefs)

        # --- URL única de PDP ---
        url = opts.get("url")
        if url:
            pdp_urls.append(url)

        # --- categorías de --category ---
        cats = opts.get("category") or []
        if cats:
            with get_client() as client:
                for c_url in cats:
                    self.stdout.write(f"[CATEG] Rastreo: {c_url}")
                    hrefs = plp_collect_all(client, c_url, limit=limit, sleep_s=sleep_s, max_pages=15)
                    pdp_urls.extend(hrefs)

        # --- categorías por defecto ---
        if opts.get("all"):
            with get_client() as client:
                for c_url in DEFAULT_CATEGORIES:
                    self.stdout.write(f"[CATEG] Rastreo: {c_url}")
                    hrefs = plp_collect_all(client, c_url, limit=limit, sleep_s=sleep_s)
                    pdp_urls.extend(hrefs)

        # Unifica y limita
        seen = set()
        unique_urls = []
        for u in pdp_urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)

        if limit and len(unique_urls) > limit:
            unique_urls = unique_urls[:limit]

        self.stdout.write(self.style.NOTICE(f"Total de PDP a procesar: {len(unique_urls)}"))

        processed = 0

        # Si no hay PDPs, refresca lo existente en SupplierProduct
        if not unique_urls:
            qs = SupplierProduct.objects.filter(supplier="supermex").order_by("-last_seen")
            if limit:
                qs = qs[:limit]
            for sp in qs:
                obj = upsert_product(sp.product_url)
                self._sync_product_and_map(obj, markup_pct, min_virtual, dry)
                self.updated_count += 1        # <— usa self.
                processed += 1
                close_old_connections()

            self.stdout.write(self.style.SUCCESS(f"Actualizados existentes: {processed}"))
            self.stdout.write(self.style.SUCCESS(
                f"Creados nuevos: {self.created_count} | Actualizados existentes: {self.updated_count}"
            ))
            return

        # Procesa las PDPs recolectadas
        for i, u in enumerate(unique_urls, start=1):
            self.stdout.write(f"[{i}/{len(unique_urls)}] upsert {u}")
            try:
                sp = upsert_product(u)  # lee/actualiza SupplierProduct y devuelve el objeto

                # ¿Existe ya un Producto con ese SKU?
                prod = Producto.objects.filter(sku=sp.supplier_sku).first()

                if not prod:
                    if sp.price_supplier is None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"[SKIP] {sp.supplier_sku} sin precio; no se crea Producto"
                            )
                        )
                        continue
                    # Crear nuevo Producto desde SupplierProduct
                    if not dry:
                        prod = create_or_update_producto_from_supplier(sp)
                    self.created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[NEW] Producto creado desde proveedor (SKU {sp.supplier_sku})"
                        )
                    )
                else:
                    # Actualizar existente: precio + stock + estado + categorías + galería
                    if not dry:
                        if sp.price_supplier is not None:
                            new_price = apply_markup_pct(sp.price_supplier, markup_pct)
                        else:
                            new_price = prod.precio_normal
                            self.stdout.write(
                                self.style.WARNING(
                                    f"[SKU {sp.supplier_sku}] sin precio; se mantiene precio actual"
                                )
                            )

                        # qty efectiva (qty real si está, si no mínimo virtual si hay stock)
                        if sp.in_stock:
                            qty = int(getattr(sp, "available_qty", 0) or MIN_VIRTUAL)
                        else:
                            qty = 0
                        estado_inv = "en_existencia" if qty > 0 else "agotado"

                        updates = []
                        if sp.price_supplier is not None and prod.precio_normal != new_price:
                            prod.precio_normal = new_price
                            updates.append("precio_normal")
                        if prod.stock != qty:
                            prod.stock = qty
                            updates.append("stock")
                        if prod.estado_inventario != estado_inv:
                            prod.estado_inventario = estado_inv
                            updates.append("estado_inventario")
                        if updates:
                            retry_save(prod, update_fields=updates)

                        # Categorías (breadcrumb) y galería (imágenes 2..n)
                        try:
                            with httpx.Client(follow_redirects=True, timeout=30) as c:
                                r = c.get(sp.product_url)
                                r.raise_for_status()
                                html = r.text
                            cats = _extract_categories_from_html(html)
                            if cats:
                                _ensure_categories(prod, cats)
                        except Exception:
                            pass
                        try:
                            _ensure_gallery(prod, sp)
                        except Exception:
                            pass

                    self.updated_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"ERROR en {u}: {e}"))

            processed += 1
            close_old_connections()
            time.sleep(sleep_s)

        # Resumen final
        self.stdout.write(self.style.SUCCESS(
            f"Creados nuevos: {self.created_count} | Actualizados existentes: {self.updated_count}"
        ))


    def _sync_product_and_map(self, sp: SupplierProduct, markup_pct: Decimal, min_virtual: int, dry: bool):
        """
        - Si no existe Producto con el SKU -> lo crea (bootstrap) desde SupplierProduct.
        - Si existe -> actualiza precio/stock y asegura el ProductSupplierMap.
        """
        sku = (sp.supplier_sku or "").strip()
        if not sku:
            self.stdout.write(self.style.WARNING("SupplierProduct sin SKU. Omitido."))
            return

        # Intentar conseguir el Producto por SKU
        try:
            producto = Producto.objects.get(sku=sku)
            created_now = False
        except Producto.DoesNotExist:
            if sp.price_supplier is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"[SKIP] {sku} sin precio; no se crea Producto"
                    )
                )
                return
            if dry:
                self.stdout.write(self.style.NOTICE(f"[DRY] Crear Producto bootstrap para SKU {sku}"))
                return
            producto = create_or_update_producto_from_supplier(sp)
            if not producto:
                return
            self.created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[NEW] Producto#{producto.id} creado desde proveedor (SKU {sku})"
                )
            )
            return  # ya quedó creado y mapeado; en próximos syncs se actualizará

        # Si ya existe, garantizamos el map
        if not ProductSupplierMap.objects.filter(product=producto, supplier_sku=sku, supplier="supermex").exists():
            if dry:
                self.stdout.write(self.style.NOTICE(f"[DRY] Crear map para {sku} -> Producto#{producto.id}"))
            else:
                retry_create(
                    ProductSupplierMap.objects,
                    product=producto,
                    supplier="supermex",
                    supplier_sku=sku,
                    auto_hide_when_oos=True,
                )
                self.stdout.write(self.style.SUCCESS(f"[MAP] Vinculado supplier->product para {sku}"))

        # Calcula precio con markup
        price_supplier = sp.price_supplier
        if price_supplier is not None:
            new_price = apply_markup_pct(price_supplier, markup_pct)
        else:
            new_price = producto.precio_normal
            self.stdout.write(
                self.style.WARNING(
                    f"[SKU {sku}] sin precio; se mantiene precio actual"
                )
            )

        # Qty efectiva
        if sp.in_stock:
            if getattr(sp, "available_qty", 0) and sp.available_qty > 0:
                qty = int(sp.available_qty)
                is_virtual = False
            else:
                qty = int(min_virtual)
                is_virtual = True
        else:
            qty = 0
            is_virtual = False

        estado_inv = "en_existencia" if qty > 0 else "agotado"

        price_log = price_supplier if price_supplier is not None else "N/A"
        sale_log = new_price if price_supplier is not None else "N/A"
        self.stdout.write(
            f"[SKU {sku}] proveedor={price_log} ⇒ venta={sale_log} | "
            f"qty={'virtual ' if is_virtual else ''}{qty} | estado={estado_inv}"
        )

        if dry:
            self.stdout.write(self.style.NOTICE("[DRY] No se guardaron cambios en Producto."))
            return

        updates = []
        if price_supplier is not None and producto.precio_normal != new_price:
            producto.precio_normal = new_price
            updates.append("precio_normal")
        if producto.stock != qty:
            producto.stock = qty
            updates.append("stock")
        if producto.estado_inventario != estado_inv:
            producto.estado_inventario = estado_inv
            updates.append("estado_inventario")

        if updates:
            retry_save(producto, update_fields=updates)
            self.updated_count += 1
            self.stdout.write(self.style.SUCCESS(f"[OK] Producto#{producto.id} actualizado: {', '.join(updates)}"))
        else:
            self.stdout.write(self.style.NOTICE("[=] Sin cambios en Producto."))

    