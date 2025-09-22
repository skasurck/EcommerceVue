# suppliers/scraper_supermex.py
from selectolax.parser import HTMLParser
import httpx, json, re
from urllib.parse import urljoin, urlsplit, urlunsplit
from decimal import Decimal
from typing import Optional
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

    # intenta pedir una cantidad muy alta para que el backend devuelva el máximo disponible
    payload_form = {
        "product_id": product_id or "",
        "product_template_id": product_template_id or "",
        "add_qty": 10000,
        "combination": "[]",
    }
    if csrf_token:
        payload_form["csrf_token"] = csrf_token

    payload_json = {
        "product_id": int(product_id) if product_id.isdigit() else product_id,
        "product_template_id": int(product_template_id) if product_template_id.isdigit() else product_template_id,
        "add_qty": 10000,
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


def _parse_price_text(price_txt: str) -> Optional[Decimal]:
    """Parsea un texto de precio a Decimal sin dividir por 100."""
    if not price_txt:
        return None

    # Quita símbolos de moneda y espacios (incluyendo NBSP)
    txt = (
        price_txt.replace("\xa0", " ")
        .replace("MXN", "")
        .replace("$", "")
        .strip()
    )
    # Solo deja dígitos y separadores
    txt = re.sub(r"[^\d.,]", "", txt)
    if not txt:
        return None

    if "," in txt and "." in txt:
        if txt.rfind(".") > txt.rfind(","):
            # formato en-US: coma miles, punto decimales
            txt = txt.replace(",", "")
        else:
            # formato en-ES: punto miles, coma decimales
            txt = txt.replace(".", "").replace(",", ".")
    elif "," in txt:
        parts = txt.split(",")
        if len(parts[-1]) == 3 and txt.count(",") == 1:
            # coma como miles
            txt = "".join(parts)
        else:
            # coma decimal
            txt = txt.replace(",", ".")
    elif "." in txt:
        parts = txt.split(".")
        if len(parts[-1]) == 3 and txt.count(".") == 1:
            # punto como miles
            txt = "".join(parts)
        # de lo contrario, punto decimal
    try:
        return Decimal(txt)
    except Exception:
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

def parse_pdp(html: str, url: str = "") -> dict:
    from selectolax.parser import HTMLParser
    t = HTMLParser(html)
    price_node = None  # inicializa para evitar referencias antes de asignar

    # --- nombre
    name_node = t.css_first("h1[itemprop='name'], h1, .product-title")
    name = name_node.text(strip=True) if name_node else ""
    sec = t.css_first("section#product_detail")
    if not (name_node and sec):
        raise ValueError("La página no parece una PDP (producto).")

    tracking_info: dict | list | None = {}
    raw_tracking = sec.attributes.get("data-product-tracking-info") if sec else None
    if raw_tracking:
        try:
            parsed_tracking = json.loads(raw_tracking)
            if isinstance(parsed_tracking, dict):
                tracking_info = parsed_tracking
            elif isinstance(parsed_tracking, list):
                tracking_info = parsed_tracking
        except Exception:
            tracking_info = {}

    # --- sku
    sku = ""
    tracking_dict = tracking_info if isinstance(tracking_info, dict) else None
    if not tracking_dict and isinstance(tracking_info, list):
        for item in tracking_info:
            if isinstance(item, dict):
                tracking_dict = item
                break
    if tracking_dict:
        sku = str(tracking_dict.get("item_id") or "").strip()
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
    price_txt = ""

    selectors = [
        "[itemprop='price']",
        ".oe_price .oe_currency_value",
        ".current-price [itemprop='price']",
        ".product_price .oe_currency_value",
        ".product-price .oe_currency_value",
        "[data-oe-type='monetary'] .oe_currency_value",
        ".price .oe_currency_value",
    ]
    for sel in selectors:
        node = t.css_first(sel)
        if not node:
            continue
        # evita precios tachados
        if node.tag in {"del", "s", "strike"}:
            continue
        parent = node.parent
        if parent and parent.tag in {"del", "s", "strike"}:
            continue
        txt = node.attributes.get("content") or node.text(separator=" ", strip=True)
        if txt:
            price_node = node
            price_txt = txt.strip()
            break

    # Fallback genérico: buscar cualquier nodo con posible monto
    if not price_txt:
        for node in t.css("span, div, p, b, strong, h2, h3, h4"):
            txt = node.text(separator=" ", strip=True)
            if not txt:
                continue
            if not re.search(r"\d", txt):
                continue
            if node.tag in {"del", "s", "strike"}:
                continue
            parent = node.parent
            if parent and parent.tag in {"del", "s", "strike"}:
                continue
            if re.search(r"\$|mxn|\d", txt, re.I):
                price_node = node
                price_txt = txt.strip()
                break

    raw_price_txt = price_txt  # para logs
    price_supplier = _parse_price_text(price_txt)

    if price_supplier is None:
        print(
            f"[WARN] [PDP] {url} price_node={'sí' if price_node else 'no'} raw='{raw_price_txt}' parsed=None"
        )
    else:
        print(
            f"[PDP] {url} price_node={'sí' if price_node else 'no'} raw='{raw_price_txt}' parsed={price_supplier}"
        )


    # --- stock
    qty: Optional[int] = None
    in_stock: Optional[bool] = None
    avail_source = "fallback"

    NEGATIVE_KEYWORDS = [
        "agotado",
        "sin existencias",
        "sin existencia",
        "sin stock",
        "sin inventario",
        "sin disponibilidad",
        "no disponible",
        "no disponible temporalmente",
        "no esta disponible",
        "no está disponible",
        "no se encuentra disponible",
        "no hay stock",
        "no hay existencias",
        "no hay inventario",
        "temporalmente agotado",
        "agotado temporalmente",
        "producto no disponible",
        "out of stock",
        "out_of_stock",
        "out-of-stock",
        "sold out",
        "sold-out",
        "soldout",
        "not available",
        "not in stock",
        "without stock",
    ]
    POSITIVE_KEYWORDS = [
        "en existencia",
        "en existencias",
        "en stock",
        "hay existencias",
        "disponible",
        "disponibles",
        "stock disponible",
        "stock en tienda",
        "stock al momento",
        "available",
        "in stock",
        "instock",
    ]
    AVAILABILITY_SELECTORS = [
        "#product_stock_availability",
        "#product_stock",
        "#availability_messages",
        "#inventory_availability",
        ".o_wsale_stock_message",
        ".o_wsale_product_availability",
        ".o_wsale_stock_container",
        ".oe_website_sale_stock_message",
        ".oe_website_sale_stock_warning",
        ".oe_website_sale_stock_container",
    ]

    def _normalize_spaces(text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def _availability_from_text(text: str, source: str) -> bool:
        nonlocal in_stock, qty, avail_source
        normalized = _normalize_spaces(text)
        if not normalized:
            return False
        lowered = normalized.lower()
        if any(neg in lowered for neg in NEGATIVE_KEYWORDS):
            in_stock = False
            qty = 0
            avail_source = source
            print(f"[AVAIL] {source} → agotado (texto)")
            return True

        qty_match = re.search(
            r"(?:existencias?|stock|disponibles?|piezas?|pzas?|pz|unidades?|uds?)\D*(\d+)",
            lowered,
        )
        if not qty_match:
            qty_match = re.search(r"\b(\d+)\b(?=\s*(?:pz|pzas?|piezas?|unidades?|uds?\b))", lowered)
        if not qty_match:
            qty_match = re.search(r"[:=]\s*(\d+)", lowered)
        qty_candidate = _to_int(qty_match.group(1)) if qty_match else None
        if qty_candidate is None and lowered.isdigit():
            qty_candidate = _to_int(lowered)

        stop = False
        if qty_candidate is not None:
            qty = qty_candidate
            avail_source = source
            if qty_candidate <= 0:
                in_stock = False
                qty = 0
                print(f"[AVAIL] {source} → qty=0")
                return True
            if in_stock is None:
                in_stock = qty_candidate > 0
                print(f"[AVAIL] {source} → qty={qty_candidate}")
            stop = True

        if in_stock is None and any(pos in lowered for pos in POSITIVE_KEYWORDS):
            in_stock = True
            avail_source = source
            print(f"[AVAIL] {source} → in_stock=True")

        return stop

    # 1) DOM: mensajes explícitos de agotado
    oos_selectors = [
        "#out_of_stock_message",
        "#product_stock_availability #out_of_stock_message",
    ]
    for sel in oos_selectors:
        node = t.css_first(sel)
        if node:
            in_stock = False
            qty = 0
            avail_source = "DOM"
            print("[AVAIL] DOM #out_of_stock_message → qty=0")
            break

    # 2) Datos en data-product-tracking-info
    if in_stock is None:
        tracking_candidates: list[dict] = []
        if isinstance(tracking_dict, dict):
            tracking_candidates.append(tracking_dict)
            for key in ("product", "item", "data"):
                nested = tracking_dict.get(key)
                if isinstance(nested, dict):
                    tracking_candidates.append(nested)
        if isinstance(tracking_info, list):
            for item in tracking_info:
                if isinstance(item, dict) and item not in tracking_candidates:
                    tracking_candidates.append(item)

        for info_dict in tracking_candidates:
            status_val = ""
            for key in (
                "item_availability",
                "availability",
                "availability_state",
                "stock_state",
                "state",
            ):
                val = info_dict.get(key)
                if isinstance(val, str) and val.strip():
                    status_val = val.strip()
                    break
            if status_val:
                status_lower = status_val.lower()
                if any(neg in status_lower for neg in NEGATIVE_KEYWORDS):
                    in_stock = False
                    qty = 0
                    avail_source = "TRACKING"
                    print("[AVAIL] tracking info → agotado")
                    break
                if in_stock is None and any(
                    pos in status_lower for pos in POSITIVE_KEYWORDS
                ):
                    in_stock = True
                    avail_source = "TRACKING"

            if qty is None or in_stock is None:
                for key in (
                    "available_qty",
                    "available_quantity",
                    "quantity_available",
                    "qty_available",
                    "virtual_available",
                    "free_qty",
                    "stock_qty",
                    "stock_on_hand",
                ):
                    val = info_dict.get(key)
                    if isinstance(val, dict):
                        for nested_key in ("value", "qty", "quantity", "count"):
                            if nested_key in val:
                                val = val[nested_key]
                                break
                    qty_candidate = _to_int(val)
                    if qty_candidate is not None:
                        qty = qty_candidate
                        in_stock = qty_candidate > 0
                        avail_source = "TRACKING_QTY"
                        print(f"[AVAIL] tracking info → qty={qty_candidate}")
                        break

            if in_stock is False:
                break

    # 3) Mensajes de disponibilidad en el DOM
    if in_stock is None:
        for sel in AVAILABILITY_SELECTORS:
            for node in t.css(sel):
                classes = node.attributes.get("class", "").lower()
                if any(token in classes for token in ["out_of_stock", "oe_out_of_stock", "o_out_of_stock", "stock_unavailable", "text-danger"]):
                    in_stock = False
                    qty = 0
                    avail_source = f"DOM:{sel}"
                    print(f"[AVAIL] {sel} (clase) → agotado")
                    break
                data_state = (
                    node.attributes.get("data-availability-state")
                    or node.attributes.get("data-stock-state")
                    or node.attributes.get("data-state")
                )
                if data_state:
                    lowered_state = data_state.lower()
                    if any(neg in lowered_state for neg in NEGATIVE_KEYWORDS):
                        in_stock = False
                        qty = 0
                        avail_source = f"DOM:{sel}"
                        print(f"[AVAIL] {sel} (data-state) → agotado")
                        break
                    if in_stock is None and any(
                        pos in lowered_state for pos in POSITIVE_KEYWORDS
                    ):
                        in_stock = True
                        avail_source = f"DOM:{sel}"

                text = node.text(separator=" ", strip=True)
                if text and _availability_from_text(text, f"DOM:{sel}"):
                    break

            if in_stock is False:
                break

    # 4) Mensajes de notificación "avísame cuando vuelva"
    if in_stock is None:
        notif_node = t.css_first("#stock_notification_div") or t.css_first(
            "#product_stock_notification_message"
        )
        if (
            notif_node
            and "back in stock" in notif_node.text(separator=" ", strip=True).lower()
            and "d-none" not in notif_node.attributes.get("class", "")
        ):
            in_stock = False
            qty = 0
            avail_source = "DOM"
            print("[AVAIL] DOM notify-back-in-stock → qty=0")

    if in_stock is None:
        text_all = t.root.text(separator=" ", strip=True).lower() if t.root else ""
        if any(neg in text_all for neg in NEGATIVE_KEYWORDS):
            in_stock = False
            qty = 0
            avail_source = "DOM"
            print("[AVAIL] DOM text out-of-stock → qty=0")

    # 5) JSON-LD (solo si el DOM no decidió)
    if in_stock is None:
        for script in t.css("script[type='application/ld+json']"):
            try:
                data = json.loads(script.text())
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict) or item.get("@type") != "Product":
                    continue
                offers = item.get("offers")
                offer_list = offers if isinstance(offers, list) else [offers] if offers else []
                for offer in offer_list:
                    availability = str((offer or {}).get("availability", ""))
                    if "OutOfStock" in availability:
                        in_stock = False
                        qty = 0
                        avail_source = "JSONLD"
                        print("[AVAIL] JSON-LD OutOfStock")
                        break
                    if "InStock" in availability:
                        in_stock = True
                        avail_source = "JSONLD"
                        print("[AVAIL] JSON-LD InStock")
                        break
                if in_stock is not None:
                    break
            if in_stock is not None:
                break

    # Qty real (opcional)
    qty_script = extract_qty_from_scripts(html)
    if qty_script is not None:
        print(f"[QTY] available_qty = {qty_script}")
        if qty_script > 0 and in_stock is not False:
            qty = qty_script
            in_stock = True
        else:
            in_stock = False
            qty = 0

    if in_stock is None:
        in_stock = True
        avail_source = avail_source or "fallback"
        print("[AVAIL] fallback → in_stock=True")

    if in_stock is False:
        qty = 0

    in_stock = bool(in_stock)

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

    return sku, name, price_supplier, in_stock, description_html, imgs, qty, avail_source

def checksum_record(data: dict) -> str:
    blob = "|".join(str(data[k]) for k in sorted(data.keys()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

def upsert_product(url: str):
    c = get_client()
    try:
        html = get_with(c, url)
        (
            sku,
            name,
            price_supplier,
            in_stock,
            description_html,
            imgs,
            qty,
            avail_source,
        ) = parse_pdp(html, url)

        # Fallback: saca el SKU del URL si vino vacío
        if not sku:
            m = re.search(r"/shop/(\d+)-", url)
            if m:
                sku = m.group(1)
            else:
                # último recurso: hash corto del URL para no romper update_or_create
                sku = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

        # si qty no vino en texto y el producto aparenta tener stock, intenta AJAX
        if qty is None and in_stock:
            ajax_qty = fetch_qty_via_ajax(c, html)
            if isinstance(ajax_qty, int) and ajax_qty >= 0:
                qty = ajax_qty
                in_stock = ajax_qty > 0
                print(f"[QTY] AJAX available_qty = {qty}")

        data = {
            "sku": sku,
            "name": name,
            "price": str(price_supplier) if price_supplier is not None else "",
            "in_stock": in_stock,
            "url": url,
            "img_count": len(imgs),
        }
        ch = checksum_record(data)

        defaults = {
            "supplier": "supermex",
            "product_url": url,
            "name": name,
            "description_html": description_html,
            "image_urls": imgs[:8],
            "in_stock": in_stock,
            # `available_qty` es NOT NULL en la base de datos; si no se pudo
            # determinar la cantidad, se guarda 0 para evitar errores
            "available_qty": qty if isinstance(qty, int) and qty >= 0 else 0,
            "last_seen": timezone.now(),
            "checksum": ch,
        }
        if price_supplier is not None:
            defaults["price_supplier"] = price_supplier

        obj, _ = _db_retry(
            SupplierProduct.objects.update_or_create,
            supplier_sku=sku,
            defaults=defaults,
        )
        obj.refresh_from_db()
        print(f"[PDP] {url} → in_stock={in_stock} qty={qty} (source={avail_source})")
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

