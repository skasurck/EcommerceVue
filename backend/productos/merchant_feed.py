"""
Feed XML para Google Merchant Center.

Genera un feed RSS 2.0 con el namespace de Google para todos los productos
activos (visibilidad=True, estado="publicado", stock > 0).

URL: GET /api/merchant-feed.xml
     GET /api/merchant-feed.xml?all=1  (incluye productos agotados)

Google valida este feed en:
https://merchants.google.com/mc/feeds/datasources
"""
import re
from django.http import HttpResponse
from django.utils.xmlutils import SimplerXMLGenerator
from io import StringIO

from .models import Producto


_HTML_TAG_RE = re.compile(r'<[^>]+>')


def _clean(text: str, max_len: int = 0) -> str:
    """Quita etiquetas HTML y recorta al límite indicado."""
    text = _HTML_TAG_RE.sub('', str(text or '')).strip()
    if max_len and len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0]
    return text


def merchant_feed_view(request):
    include_all = request.GET.get('all') == '1'

    qs = (
        Producto.objects
        .filter(visibilidad=True, estado='publicado')
        .select_related('marca')
        .prefetch_related('categorias')
        .only(
            'id', 'slug', 'nombre', 'descripcion_corta', 'descripcion_larga',
            'imagen_principal', 'precio_normal', 'precio_rebajado',
            'stock', 'estado_inventario', 'sku', 'marca',
        )
        .order_by('-fecha_creacion')
    )

    if not include_all:
        qs = qs.filter(stock__gt=0)

    origin = f"{request.scheme}://{request.get_host()}"

    out = StringIO()
    xml = SimplerXMLGenerator(out, encoding='utf-8', short_empty_elements=True)
    xml.startDocument()

    xml.startElement('rss', {
        'version': '2.0',
        'xmlns:g': 'http://base.google.com/ns/1.0',
    })
    xml.startElement('channel', {})

    xml.startElement('title', {})
    xml.characters('Mktska Digital — Productos')
    xml.endElement('title')

    xml.startElement('link', {})
    xml.characters(origin)
    xml.endElement('link')

    xml.startElement('description', {})
    xml.characters('Feed de productos para Google Merchant Center')
    xml.endElement('description')

    for p in qs:
        xml.startElement('item', {})

        # ── Campos requeridos ──────────────────────────────────────────────────
        _tag(xml, 'g:id', p.sku or str(p.id))

        nombre_limpio = _clean(p.nombre, 150)
        _tag(xml, 'g:title', nombre_limpio)

        desc = _clean(p.descripcion_larga or p.descripcion_corta or nombre_limpio, 5000)
        _tag(xml, 'g:description', desc or nombre_limpio)

        _tag(xml, 'g:link', f"{origin}/producto/{p.slug}")

        if p.imagen_principal:
            img_url = request.build_absolute_uri(p.imagen_principal.url)
            _tag(xml, 'g:image_link', img_url)

        _tag(xml, 'g:condition', 'new')

        availability = (
            'in_stock'
            if p.estado_inventario == 'en_existencia' or p.stock > 0
            else 'out_of_stock'
        )
        _tag(xml, 'g:availability', availability)

        # Precio base (requerido)
        precio_normal = float(p.precio_normal or 0)
        _tag(xml, 'g:price', f'{precio_normal:.2f} MXN')

        # Precio rebajado (opcional)
        if p.precio_rebajado and float(p.precio_rebajado) < precio_normal:
            _tag(xml, 'g:sale_price', f'{float(p.precio_rebajado):.2f} MXN')

        # ── Campos recomendados ────────────────────────────────────────────────
        if p.marca:
            _tag(xml, 'g:brand', _clean(p.marca.nombre, 70))

        if p.sku:
            _tag(xml, 'g:mpn', p.sku)

        # Categoría Google (primera categoría disponible)
        cats = list(p.categorias.all())
        if cats:
            _tag(xml, 'g:product_type', _clean(cats[0].nombre, 750))

        xml.endElement('item')

    xml.endElement('channel')
    xml.endElement('rss')

    return HttpResponse(out.getvalue(), content_type='application/xml; charset=utf-8')


def _tag(xml: SimplerXMLGenerator, name: str, value: str) -> None:
    xml.startElement(name, {})
    xml.characters(value)
    xml.endElement(name)
