"""
Vista SEO para páginas de producto.

Para navegadores normales: sirve el index.html del build de Vue (el router
de Vue toma el control y carga el producto normalmente).

Para bots de redes sociales (WhatsApp, Facebook, Twitter, etc.):
inyecta <title>, <meta description> y Open Graph tags con los datos reales
del producto, para que la vista previa del link sea correcta.
"""
import re
import html as html_lib
from pathlib import Path

_LOWERCASE_WORDS = frozenset([
    'de', 'del', 'la', 'las', 'los', 'el', 'un', 'una', 'unos', 'unas',
    'con', 'para', 'por', 'sin', 'sobre', 'entre', 'y', 'o', 'a', 'en',
])

def _to_product_title(text: str) -> str:
    """Convierte nombre en MAYÚSCULAS a Title Case manteniendo códigos técnicos."""
    words = text.strip().lower().split()
    result = []
    for i, word in enumerate(words):
        if any(c.isdigit() for c in word):
            result.append(word.upper())
        elif i > 0 and word in _LOWERCASE_WORDS:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

from django.conf import settings
from django.http import HttpResponse, Http404

from .models import Producto

# User-Agents de bots de redes sociales y crawlers
_BOT_RE = re.compile(
    r'(facebookexternalhit|Twitterbot|WhatsApp|LinkedInBot|TelegramBot|'
    r'Slackbot|Discordbot|Googlebot|bingbot|Baiduspider|YandexBot|'
    r'DuckDuckBot|Applebot|redditbot|Pinterest|vkShare|W3C_Validator)',
    re.IGNORECASE,
)

# Ruta al index.html del build de Vue (ajusta si cambia la estructura)
_DIST_INDEX = Path(settings.BASE_DIR).parent / 'frontend' / 'dist' / 'index.html'


def _e(text: str) -> str:
    """Escapa caracteres HTML para uso seguro en atributos y texto."""
    return html_lib.escape(str(text or ''), quote=True)


def producto_seo_view(request, pk: int):
    # Leer el index.html compilado de Vue
    try:
        html = _DIST_INDEX.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise Http404('Build de frontend no encontrado')

    ua = request.META.get('HTTP_USER_AGENT', '')
    if not _BOT_RE.search(ua):
        # Usuario normal: Vue maneja todo, servir index.html sin cambios
        return HttpResponse(html, content_type='text/html')

    # Es un bot: inyectar meta tags con datos reales del producto
    try:
        producto = (
            Producto.objects
            .select_related('marca')
            .only('id', 'slug', 'nombre', 'descripcion_corta', 'descripcion_larga',
                  'imagen_principal', 'precio_normal', 'precio_rebajado',
                  'stock', 'marca', 'sku')
            .get(pk=pk, visibilidad=True)
        )
    except Producto.DoesNotExist:
        # Producto no existe o no es visible: servir index.html sin cambios
        return HttpResponse(html, content_type='text/html')

    # Construir URLs absolutas
    origin = f"{request.scheme}://{request.get_host()}"
    product_url = f"{origin}/producto/{producto.slug}/"

    if producto.imagen_principal:
        image_url = request.build_absolute_uri(producto.imagen_principal.url)
    else:
        image_url = f"{origin}/logo-mktska.png"

    desc_raw = (producto.descripcion_larga or producto.descripcion_corta or '').strip()
    # Quitar tags HTML si la descripción los tiene
    desc_raw = re.sub(r'<[^>]+>', '', desc_raw)[:160]

    nombre = _e(_to_product_title(producto.nombre))
    desc   = _e(desc_raw)
    img    = _e(image_url)
    url    = _e(product_url)

    og_tags = (
        f'<title>{nombre} | Mktska Digital</title>\n'
        f'    <meta name="description" content="{desc}">\n'
        f'    <meta property="og:type" content="product">\n'
        f'    <meta property="og:url" content="{url}">\n'
        f'    <meta property="og:title" content="{nombre}">\n'
        f'    <meta property="og:description" content="{desc}">\n'
        f'    <meta property="og:image" content="{img}">\n'
        f'    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{nombre}">\n'
        f'    <meta name="twitter:description" content="{desc}">\n'
        f'    <meta name="twitter:image" content="{img}">\n'
    )

    # Reemplazar el <title> estático y agregar OG tags antes de </head>
    html = re.sub(r'<title>[^<]*</title>', '', html, count=1)
    html = re.sub(r'<meta name="description"[^>]*>', '', html, count=1)
    html = html.replace('</head>', f'    {og_tags}</head>', 1)

    return HttpResponse(html, content_type='text/html')
