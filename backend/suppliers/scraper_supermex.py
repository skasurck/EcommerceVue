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
        except httpx.HTTPStatusError as exc:
            # 404 y 410 son definitivos, no tiene sentido reintentar
            if exc.response.status_code in (404, 410):
                raise
            if attempt == retries - 1:
                raise
            time.sleep(1 * (2 ** attempt))
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

def extract_ids_and_csrf(html: str, url: str = ""):
    """
    Lee product_id, product_template_id y csrf del HTML de forma más robusta.
    Agrega logs para depuración.
    """
    t = HTMLParser(html)
    
    # Búsqueda mejorada de IDs
    pid_node = t.css_first("input.product_id, input[name='product_id']")
    product_id = pid_node.attributes.get("value", "").strip() if pid_node else ""
    
    ptid_node = t.css_first("input.product_template_id, input[name='product_template_id']")
    product_template_id = ptid_node.attributes.get("value", "").strip() if ptid_node else ""

    source = "input" if product_id or product_template_id else "not-found"

    # Fallback: buscar en atributos data-* si no se encontraron en inputs
    if not product_id:
        # Odoo a menudo pone el ID en un `data-product-id` en un `div` o `form`
        node_with_data_id = t.css_first("[data-product-id]")
        if node_with_data_id:
            product_id = node_with_data_id.attributes.get("data-product-id", "").strip()
            if source == "not-found": source = "data-attribute"

    if not product_template_id:
        node_with_data_template_id = t.css_first("[data-product-template-id]")
        if node_with_data_template_id:
            product_template_id = node_with_data_template_id.attributes.get("data-product-template-id", "").strip()
            if source == "not-found": source = "data-attribute"

    # CSRF Token
    csrf_node = t.css_first("input[name='csrf_token']")
    csrf_token = csrf_node.attributes.get("value", "").strip() if csrf_node else ""

    print(f"[DEBUG] ID Extraction ({url}): "
          f"product_id='{product_id}', "
          f"product_template_id='{product_template_id}', "
          f"csrf_token={'present' if csrf_token else 'missing'}, "
          f"source='{source}'")

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

def fetch_qty_via_ajax(c: httpx.Client, html: str, url: str):
    """
    Intenta obtener el stock via AJAX, imitando la petición exacta del navegador.
    """
    product_id, product_template_id, csrf_token = extract_ids_and_csrf(html, url=url)

    if not product_id or not product_id.isdigit():
        print(f"[DEBUG] AJAX ({url}): No se encontró un product_id válido. Abortando.")
        return None
    
    if not product_template_id or not product_template_id.isdigit():
        print(f"[DEBUG] AJAX ({url}): No se encontró un product_template_id válido. Abortando.")
        return None

    # Payload exacto observado en el navegador
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_template_id": int(product_template_id),
            "product_id": int(product_id),
            "combination": [],
            "add_qty": 1,
            "parent_combination": []
        },
        "id": int(time.time() * 1000)
    }

    # Endpoint exacto observado
    ajax_url = urljoin(BASE, "/website_sale/get_combination_info")
    
    # Cabeceras que imitan a un navegador
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": url,
        "Content-Type": "application/json",
    }

    try:
        print(f"[DEBUG] AJAX ({url}): POST {ajax_url} con payload {payload['params']}")
        r = c.post(ajax_url, json=payload, headers=headers)
        
        if r.status_code == 200:
            js = r.json()
            if "error" in js:
                print(f"[DEBUG] AJAX ({url}): Respuesta OK pero con error Odoo. JSON: {r.text[:300]}")
                return None

            qty = _extract_qty_from_json(js)
            if qty is not None:
                print(f"[DEBUG] AJAX ({url}): Éxito. Qty={qty}")
                return qty
            else:
                print(f"[DEBUG] AJAX ({url}): Respuesta OK pero sin 'free_qty' esperado. JSON: {r.text[:300]}")
        else:
            print(f"[DEBUG] AJAX ({url}): Falló. Status={r.status_code}, Body: {r.text[:300]}")

    except Exception as e:
        print(f"[DEBUG] AJAX ({url}): Excepción en {ajax_url}: {e}")

    print(f"[DEBUG] AJAX ({url}): No se pudo obtener el stock vía AJAX.")
    return None

def _extract_qty_from_json(js: dict):
    if not isinstance(js, dict):
        return None

    # Check if the JSON is wrapped in a 'jsonrpc' structure
    if "result" in js and isinstance(js["result"], dict):
        js = js["result"]

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
        value = Decimal(txt)
        # Sanity check: ningún producto de Supermex cuesta más de 500,000 MXN
        # Si supera ese límite es un error de parseo (ej: nombre del producto tomado como precio)
        if value <= 0 or value > Decimal("500000"):
            return None
        return value
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
        u = _strip_query(u)
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

    # --- CONSTANTES Y FUNCIONES DE AYUDA ---
    NEGATIVE_KEYWORDS = [
        "agotado", "sin existencias", "sin stock", "no disponible", "out of stock",
        "no disponible por el momento", "producto no disponible", "out of stock",
        "no longer available", "this product is no longer available",
        "product is no longer available", "ya no está disponible",
    ]
    POSITIVE_KEYWORDS = [
        "en existencia", "en stock", "disponible", "available", "in stock",
    ]
    AVAILABILITY_SELECTORS = [
        "#product_stock_availability", ".o_wsale_stock_message",
        ".o_wsale_product_availability", ".oe_website_sale_stock_message",
    ]
    HIDDEN_CLASS_TOKENS = {
        "d-none", "o_hidden", "o_invisible", "oe_hidden", "o_is_hidden",
        "visually-hidden", "sr-only", "collapse",
    }

    def _normalize_spaces(text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def _node_is_hidden(node) -> bool:
        current = node
        while current is not None:
            attrs = getattr(current, "attributes", {}) or {}
            cls = attrs.get("class", "").lower()
            if cls:
                tokens = {
                    tok.strip()
                    for tok in cls.replace("\xa0", " ").split()
                    if tok.strip()
                }
                if tokens & HIDDEN_CLASS_TOKENS:
                    return True
            style = attrs.get("style", "").replace(" ", "").lower()
            if style:
                if "display:none" in style or "visibility:hidden" in style:
                    return True
            if "hidden" in attrs or attrs.get("aria-hidden") == "true":
                return True
            current = current.parent
        return False

    def _availability_from_text(text: str, source: str) -> bool:
        nonlocal in_stock, qty, avail_source
        lowered = _normalize_spaces(text).lower()
        if any(neg in lowered for neg in NEGATIVE_KEYWORDS):
            in_stock = False
            qty = 0
            avail_source = source
            print(f"[AVAIL] {source} → agotado (texto)")
            return True
        if in_stock is None and any(pos in lowered for pos in POSITIVE_KEYWORDS):
            in_stock = True
            avail_source = source
            print(f"[AVAIL] {source} → in_stock=True")
        return in_stock is not None

    # --- INICIO DE PARSEO ---
    # ... (nombre, sku, precio - SIN CAMBIOS) ...
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

    # Fallback genérico: solo nodos que explícitamente muestren un precio con símbolo de moneda
    if not price_txt:
        for node in t.css("span, div, p, b, strong, h2, h3, h4"):
            txt = node.text(separator=" ", strip=True)
            if not txt:
                continue
            if node.tag in {"del", "s", "strike"}:
                continue
            parent = node.parent
            if parent and parent.tag in {"del", "s", "strike"}:
                continue
            # Requiere símbolo de moneda ($, MXN) junto a dígitos para evitar
            # capturar textos como "30-day guarantee" o "2-3 Business Days"
            if re.search(r"(\$\s*[\d,]+|[\d,]+\s*mxn|mxn\s*[\d,]+)", txt, re.I):
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


    # 1) Detección de agotado por elementos inequívocos
    oos_selectors = [
        "#out_of_stock_message", # Tu elemento claro
        "#product_stock_availability #out_of_stock_message",
    ]
    cta_wrapper = t.css_first("#o_wsale_cta_wrapper")
    
    # PRIORITY 1: #out_of_stock_message (incluso si está oculto, si está en el DOM, Odoo lo pone)
    if t.css_first("#out_of_stock_message"):
        in_stock = False
        qty = 0
        avail_source = "DOM:OOS_MESSAGE"
        print("[AVAIL] DOM #out_of_stock_message → qty=0")

    # PRIORITY 2: Botón CTA oculto y con clase de agotado
    elif cta_wrapper and (
        "out_of_stock" in cta_wrapper.attributes.get("class", "").lower()
        or _node_is_hidden(cta_wrapper)
    ):
        in_stock = False
        qty = 0
        avail_source = "DOM:cta_wrapper"
        print("[AVAIL] CTA wrapper oculto/out_of_stock → qty=0")

    # 2) Datos en data-product-tracking-info (sigue siendo útil)
    if in_stock is None:
        # ... (Mantener lógica de detección por tracking_info) ...

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
                if _node_is_hidden(node):
                    continue
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
            and not _node_is_hidden(notif_node)
            and "back in stock" in notif_node.text(separator=" ", strip=True).lower()
        ):
            in_stock = False
            qty = 0
            avail_source = "DOM:notify"
            print("[AVAIL] DOM notify-back-in-stock → qty=0")

    # 5) JSON-LD (sigue siendo útil)
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
    
    # 6) FALLBACK FINAL (Revertido a "asumir disponible" si tiene precio y falló todo)
    if in_stock is None:
        if price_supplier is not None:
            in_stock = True
            avail_source = avail_source or "fallback-price"
            print("[AVAIL] fallback-price → in_stock=True (con precio)")
        else:
            in_stock = False
            qty = 0
            avail_source = avail_source or "fallback-no-price"
            print("[AVAIL] fallback-no-price → in_stock=False/qty=0")
    
    if in_stock is False:
        qty = 0

    in_stock = bool(in_stock)

    # --- descripción y imágenes (SIN CAMBIOS) ---
    desc_node = t.css_first("#product_full_description, [itemprop='description'], .product-description")
    description_html = desc_node.html if desc_node else ""

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

        # Prioritize AJAX call for quantity
        ajax_qty = fetch_qty_via_ajax(c, html, url)
        if isinstance(ajax_qty, int) and ajax_qty >= 0:
            qty = ajax_qty
            in_stock = ajax_qty > 0
            avail_source = "ajax"
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


def sync_stock_for_product(sp, client: httpx.Client) -> dict:
    """
    Actualiza solo precio + stock de un SupplierProduct existente.
    - Si tiene odoo_product_id cacheado: llama AJAX directo (sin cargar HTML).
    - Si no: carga HTML, extrae IDs, los cachea para la próxima vez.
    Devuelve dict con los campos actualizados o lanza excepción.
    """
    url = _strip_query(sp.product_url)
    # Corregir URL sucia en DB si quedó con query string (ej: ?page=4)
    if url != sp.product_url:
        sp.product_url = url
        sp.save(update_fields=["product_url"])

    # --- Intentar AJAX directo si tenemos los IDs cacheados ---
    if sp.odoo_product_id and sp.odoo_template_id:
        payload = {
            "jsonrpc": "2.0", "method": "call",
            "params": {
                "product_template_id": sp.odoo_template_id,
                "product_id": sp.odoo_product_id,
                "combination": [], "add_qty": 1, "parent_combination": [],
            },
            "id": int(time.time() * 1000),
        }
        try:
            r = client.post(
                urljoin(BASE, "/website_sale/get_combination_info"),
                json=payload,
                headers={"X-Requested-With": "XMLHttpRequest", "Referer": url, "Content-Type": "application/json"},
            )
            if r.status_code == 200:
                js = r.json()
                if "error" not in js:
                    qty = _extract_qty_from_json(js)
                    result = js.get("result", {})
                    price_txt = str(result.get("price", "") or result.get("list_price", ""))
                    price = _parse_price_text(price_txt)
                    in_stock = (qty > 0) if isinstance(qty, int) else bool(result.get("product_is_combination_possible", True))
                    return {"price": price, "in_stock": in_stock, "qty": qty if isinstance(qty, int) else (1 if in_stock else 0), "method": "ajax_cached"}
        except Exception as exc:
            print(f"[STOCK] AJAX cacheado falló para {url}: {exc} — recargando HTML")

    # --- Fallback: cargar HTML, extraer IDs y precio/stock ---
    try:
        html = get_with(client, url)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            print(f"[STOCK] 404 en {url} → agotado/qty=0")
            return {"price": None, "in_stock": False, "qty": 0, "method": "404"}
        raise
    sku_parsed, name, price, in_stock, _, _, qty, _ = parse_pdp(html, url)
    product_id, template_id, _ = extract_ids_and_csrf(html, url)

    # Intentar AJAX con los IDs recién extraídos
    if product_id and product_id.isdigit() and template_id and template_id.isdigit():
        ajax_qty = fetch_qty_via_ajax(client, html, url)
        if isinstance(ajax_qty, int) and ajax_qty >= 0:
            qty = ajax_qty
            in_stock = ajax_qty > 0
        # Guardar IDs en caché
        sp.odoo_product_id = int(product_id)
        sp.odoo_template_id = int(template_id)
        sp.save(update_fields=["odoo_product_id", "odoo_template_id"])

    return {"price": price, "in_stock": in_stock, "qty": qty if isinstance(qty, int) else (1 if in_stock else 0), "method": "html"}


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

