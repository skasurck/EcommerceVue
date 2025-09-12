# suppliers/scraper_supermex.py
from selectolax.parser import HTMLParser
import httpx, json, re
from urllib.parse import urljoin, urlsplit, urlunsplit
from decimal import Decimal
from django.utils import timezone
from django.db.models import F
from django.db import OperationalError, close_old_connections
from .models import SupplierProduct
from .pricing import apply_markup
import hashlib, time
from httpx import Timeout

_PDP_RE = re.compile(r"/shop/\d+-")  # ej: /shop/841163081082-...

BASE = "https://www.supermexdigital.mx"

def abs_url(u: str) -> str:
    return urljoin(BASE, u)


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

def get_client(http2: bool = True) -> httpx.Client:
    # timeouts cortos y explícitos
    to = Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)
    return httpx.Client(
        headers={
            "User-Agent": "mktska-sync/1.0 (+contacto@tu-dominio)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
            "Referer": BASE + "/",
            "Connection": "keep-alive",
        },
        timeout=to,
        follow_redirects=True,
        http2=http2,
    )


def get_with(client: httpx.Client, url: str, retries: int = 3) -> str:
    # log antes del request: así verás si se queda aquí
    print(f"[HTTP] GET {url}")
    for attempt in range(retries):
        try:
            r = client.get(url)
            r.raise_for_status()
            return r.text
        except httpx.HTTPError:
            if attempt == retries - 1:
                raise
            time.sleep(1 * (2 ** attempt))

def _strip_query(u: str) -> str:
    p = urlsplit(u)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

def _to_int(v):
    try:
        return int(float(v))
    except Exception:
        return None

def extract_ids_and_csrf(html: str):
    """Lee product_id, product_template_id y csrf del HTML."""
    t = HTMLParser(html)
    pid = (t.css_first("input.product_id") or t.css_first("input[name='product_id']"))
    ptid = (t.css_first("input.product_template_id") or t.css_first("input[name='product_template_id']"))
    csrf = t.css_first("input[name='csrf_token']")
    product_id = pid.attributes.get("value", "").strip() if pid else ""
    product_template_id = ptid.attributes.get("value", "").strip() if ptid else ""
    csrf_token = csrf.attributes.get("value", "").strip() if csrf else ""
    return product_id, product_template_id, csrf_token

def extract_qty_from_scripts(html: str):
    """Busca qty en scripts embebidos (free_qty, virtual_available, stock_qty, etc.)."""
    # 1) Busca JSON crudo con campos clave
    candidates = []
    for m in re.finditer(r"\{[^{}]{0,500}(free_qty|virtual_available|stock_qty|available_qty)[^{}]{0,500}\}", html, re.I | re.S):
        candidates.append(m.group(0))
    for blob in candidates:
        try:
            js = json.loads(blob)
        except Exception:
            # a veces hay comas finales o comillas simples; intenta sanitizar lo mínimo
            js = {}
            try:
                js = json.loads(re.sub(r",\s*([}\]])", r"\1", blob))
            except Exception:
                pass
        if isinstance(js, dict):
            for k in ["free_qty", "virtual_available", "stock_qty", "available_qty", "quantity"]:
                v = js.get(k)
                v_int = _to_int(v)
                if v_int is not None and v_int >= 0:
                    return v_int
            # niveles anidados típicos
            nested = js.get("product") or js.get("combination_info") or {}
            if isinstance(nested, dict):
                for k in ["free_qty", "virtual_available", "stock_qty", "available_qty", "quantity"]:
                    v = nested.get(k)
                    v_int = _to_int(v)
                    if v_int is not None and v_int >= 0:
                        return v_int
    # 2) Regex directo “Only 4 Units… / Solo 4 Unidades…”
    text = HTMLParser(html).body.text(separator=" ", strip=True) if HTMLParser(html).body else ""
    pats = [
        r"Only\s+(\d+)\s+Units?\s+left\s+in\s+stock",
        r"Only\s+(\d+)\s+left\s+in\s+stock",
        r"Solo\s+(\d+)\s+Unidades?.*existencia",
        r"Quedan?\s+(\d+)\s+(?:piezas?|unidades?)",
        r"\b(\d+)\b\s+(?:Units?|unidades?)\b",
    ]
    for pat in pats:
        m = re.search(pat, text, re.I)
        if m:
            v_int = _to_int(m.group(1))
            if v_int is not None:
                return v_int
    return None

def fetch_qty_via_ajax(c: httpx.Client, html: str):
    """Prueba varios endpoints Odoo, con y sin /en, en form y JSON."""
    product_id, product_template_id, csrf_token = extract_ids_and_csrf(html)
    if not product_id and not product_template_id:
        return None

    payload_form = {
        "product_id": product_id or "",
        "product_template_id": product_template_id or "",
        "add_qty": 1,
        "combination": "[]",
    }
    if csrf_token:
        payload_form["csrf_token"] = csrf_token

    payload_json = {
        "product_id": int(product_id) if product_id.isdigit() else product_id,
        "product_template_id": int(product_template_id) if product_template_id.isdigit() else product_template_id,
        "add_qty": 1,
        "combination": [],
    }

    paths = [
        "/website_sale/get_combination_info",
        "/shop/get_combination_info",
        "/website_sale/get_product_data",
    ]
    prefixes = ["", "/en"]

    for pref in prefixes:
        for path in paths:
            url = urljoin(BASE, pref + path)
            # 1) POST form
            try:
                r = c.post(url, data=payload_form, headers={"X-Requested-With": "XMLHttpRequest"})
                if r.status_code == 200:
                    try:
                        js = r.json()
                    except Exception:
                        m = re.search(r"\{.*\}", r.text, re.S)
                        js = json.loads(m.group(0)) if m else {}
                    qty = _extract_qty_from_json(js)
                    if qty is not None:
                        return qty
            except Exception:
                pass
            # 2) POST JSON
            try:
                r = c.post(url, json=payload_json, headers={"X-Requested-With": "XMLHttpRequest"})
                if r.status_code == 200:
                    try:
                        js = r.json()
                    except Exception:
                        m = re.search(r"\{.*\}", r.text, re.S)
                        js = json.loads(m.group(0)) if m else {}
                    qty = _extract_qty_from_json(js)
                    if qty is not None:
                        return qty
            except Exception:
                pass
    return None

def _extract_qty_from_json(js: dict):
    if not isinstance(js, dict):
        return None
    for k in ["free_qty", "virtual_available", "stock_qty", "available_qty", "quantity"]:
        if k in js:
            v_int = _to_int(js.get(k))
            if v_int is not None and v_int >= 0:
                return v_int
    nested = js.get("product") or js.get("combination_info") or {}
    if isinstance(nested, dict):
        for k in ["free_qty", "virtual_available", "stock_qty", "available_qty", "quantity"]:
            v_int = _to_int(nested.get(k))
            if v_int is not None and v_int >= 0:
                return v_int
    return None

def parse_plp(html: str) -> list[str]:
    from selectolax.parser import HTMLParser
    t = HTMLParser(html)
    hrefs = []
    for a in t.css(
        "a.product-thumbnail, a.product-title, h2 a, "
        "a.o_wsale_product_information, a.card, "
        ".o_wsale_product_information_text a, "
        ".oe_product a, .o_wsale_products_grid a"
    ):
        href = a.attributes.get("href")
        if href:
            hrefs.append(href)

    if not hrefs:
        for a in t.css("a[href]"):
            href = a.attributes.get("href", "")
            if "/shop/" in href and "/category/" not in href:
                hrefs.append(href)
     # Normaliza y absolutiza
    out = []
    seen = set()
    for u in hrefs:
        if not u or u.startswith("#") or "javascript:" in u:
            continue
        if u.startswith("/"):
            u = abs_url(u)
        if not u.startswith("http"):
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def _hash_list(urls: list[str]) -> str:
    return hashlib.sha1("|".join(urls).encode("utf-8")).hexdigest()

def plp_collect_all(client, start_url: str, limit: int = 0, sleep_s: float = 0.6, max_pages: int = 5) -> list[str]:
    collected: list[str] = []
    seen_urls = set()

    base_url = start_url
    sep = "&" if "?" in base_url else "?"
    last_page_hash = None
    repeated_hits = 0

    for page in range(1, max_pages + 1):
        html = get_with(client, f"{base_url}{sep}page={page}")
        urls = parse_plp(html)

        page_hash = _hash_list(urls)
        if last_page_hash is not None and page_hash == last_page_hash:
            repeated_hits += 1
        else:
            repeated_hits = 0
        last_page_hash = page_hash

        new_urls = [u for u in urls if u not in seen_urls]
        if new_urls:
            collected.extend(new_urls)
            seen_urls.update(new_urls)
        print(f"[PLP] Página {page}: {len(urls)} encontrados, {len(new_urls)} nuevos, total {len(collected)}")

        if not urls or not new_urls or repeated_hits >= 1:
            print("[PLP] Corte por sin-urls / sin-nuevos / repetición. Fin.")
            break
        if limit and len(collected) >= limit:
            collected = collected[:limit]
            print(f"[PLP] Alcanzado límite global {limit}. Fin.")
            break

        time.sleep(sleep_s)

    return list(dict.fromkeys(collected))

def parse_pdp(html: str) -> dict:
    from selectolax.parser import HTMLParser
    t = HTMLParser(html)
    # --- nombre
    name_node = t.css_first("h1[itemprop='name'], h1, .product-title")
    name = name_node.text(strip=True) if name_node else ""
    sec = t.css_first("section#product_detail")
    if not (name_node and (price_node or sec)):
        raise ValueError("La página no parece una PDP (producto).")
  
  # --- sku
    sku = ""
    sec = t.css_first("section#product_detail")
    if sec and sec.attributes.get("data-product-tracking-info"):
        try:
            info = json.loads(sec.attributes["data-product-tracking-info"])
            sku = str(info.get("item_id") or "").strip()
        except Exception:
            pass
    if not sku:
        url_node = t.css_first("span[itemprop='url']")
        if url_node:
            m = re.search(r"/shop/(\d+)-", url_node.text(strip=True))
            if m:
                sku = m.group(1)
    if not sku:
        h1 = name or ""
        m = re.search(r"\b(\d{8,14})\b", h1)
        if not m:
            img0 = t.css_first(".o_wsale_product_images img, img.product_detail_img")
            if img0 and img0.attributes.get("src", ""):
                m = re.search(r"\[(\d{8,14})\]", img0.attributes["src"])
        if m:
            sku = m.group(1)

    # --- precio
    price_node = None          # <- ¡importante! inicializar antes de usar
    price_txt = ""

    # 1) itemprop="price"
    node = t.css_first("[itemprop='price']")
    if node:
        price_node = node
        price_txt = (node.attributes.get("content") or node.text(strip=True) or "").strip()

    # 2) Fallbacks Odoo
    if not price_txt:
        node = t.css_first(
            ".oe_price .oe_currency_value, "
            ".current-price [itemprop='price'], "
            ".product_price .oe_currency_value, "
            ".product-price .oe_currency_value, "
            "[data-oe-type='monetary'] .oe_currency_value"
        )
        if node:
            price_node = node
            price_txt = node.text(strip=True)

    # Normaliza y convierte
    price_txt = price_txt.replace("$", "").replace(",", "").replace("\xa0", " ")
    price_txt = re.sub(r"[^\d\.]", "", price_txt)
    try:
        price_supplier = Decimal(price_txt) if price_txt else Decimal("0")
    except Exception:
        price_supplier = Decimal("0")


    # --- stock by text (rápido)
    qty = None
    node = t.css_first("#threshold_message") or t.css_first("#product_stock_availability") or t.css_first(".availability_messages")
    texts = []
    if node: texts.append(node.text(separator=" ", strip=True))
    if t.body: texts.append(t.body.text(separator=" ", strip=True))
    pats = [
        r"Only\s+(\d+)\s+Units?\s+left\s+in\s+stock\.?",
        r"Only\s+(\d+)\s+left\s+in\s+stock\.?",
        r"Solo\s+(\d+)\s+Unidades?.*existencia",
        r"Quedan?\s+(\d+)\s+(?:piezas?|unidades?)",
        r"\b(\d+)\b\s+(?:Units?|unidades?)\b",
    ]
    for text in texts:
        for pat in pats:
            m = re.search(pat, text, re.I)
            if m:
                try:
                    qty = int(m.group(1)); break
                except: pass
        if qty is not None: break

    # --- in_stock
    if qty is not None:
        in_stock = qty > 0
    else:
        in_stock = True
        if t.css_first("#product_unavailable:not(.d-none)"):
            in_stock = False
        if t.css_first("#add_to_cart:not(.disabled)"):
            in_stock = True

    # --- descripción
    desc_node = t.css_first("#product_full_description, [itemprop='description'], .product-description")
    description_html = desc_node.html if desc_node else ""

    # --- imágenes (solo carrusel, dedup sin query)
    imgs = []
    for img in t.css(".o_wsale_product_images .carousel-inner img"):
        src = img.attributes.get("src") or img.attributes.get("data-src") or ""
        if not src: continue
        if src.startswith("/"): src = abs_url(src)
        src = _strip_query(src)
        if src not in imgs: imgs.append(src)

    return sku, name, price_supplier, in_stock, description_html, imgs, qty

def checksum_record(data: dict) -> str:
    blob = "|".join(str(data[k]) for k in sorted(data.keys()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

def upsert_product(url: str):
    c = get_client()
    try:
        html = get_with(c, url)
        sku, name, price_supplier, in_stock, description_html, imgs, qty = parse_pdp(html)

        # Fallback: saca el SKU del URL si vino vacío
        if not sku:
            m = re.search(r"/shop/(\d+)-", url)
            if m:
                sku = m.group(1)
            else:
                # último recurso: hash corto del URL para no romper update_or_create
                sku = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

        # si qty no vino en texto, intenta AJAX
        if qty is None:
            ajax_qty = fetch_qty_via_ajax(c, html)
            if isinstance(ajax_qty, int) and ajax_qty >= 0:
                qty = ajax_qty
                in_stock = ajax_qty > 0

        data = {"sku": sku, "name": name, "price": str(price_supplier),
                "in_stock": in_stock, "url": url, "img_count": len(imgs)}
        ch = checksum_record(data)

        defaults = {
            "supplier": "supermex",
            "product_url": url,
            "name": name,
            "description_html": description_html,
            "image_urls": imgs[:8],
            "price_supplier": price_supplier,
            "in_stock": in_stock,
            "last_seen": timezone.now(),
            "checksum": ch,
        }
        if qty is not None:
            defaults["available_qty"] = qty

        obj, _ = _db_retry(
            SupplierProduct.objects.update_or_create,
            supplier_sku=sku,
            defaults=defaults,
        )
        obj.refresh_from_db()
        return obj
    finally:
        c.close()


def crawl_all():
    categories = [
        "https://www.supermexdigital.mx/shop/monitores",
        "https://www.supermexdigital.mx/shop/almacenamiento",
        # agrega tus categorías clave…
    ]
    urls = set()
    for cat in categories:
        with get_client() as c:
            plp_html = get_with(c, cat)
        for u in parse_plp(plp_html):
            if u.startswith("/"): u = "https://www.supermexdigital.mx" + u
            urls.add(u)
        time.sleep(1)

    for i, url in enumerate(urls):
        upsert_product(url)
        time.sleep(1)  # rate limit

