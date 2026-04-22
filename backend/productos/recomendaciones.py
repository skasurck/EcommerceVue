"""
Endpoints de recomendaciones para PDP y Home.

Estrategia:
    1. Usar `tracking.CoOcurrenciaProducto` con prioridad
       co_purchase > co_cart > co_view.
    2. Si no alcanza, completar con productos de la(s) misma(s) categoría(s).
    3. Si todavía no alcanza, completar con destacados / populares recientes.

Todas las consultas usan `select_related`/`prefetch_related` y las anotaciones
que requiere `ProductoListSerializer` (`has_tier`, `color_atributos`) para
evitar N+1.
"""
from __future__ import annotations

from collections import OrderedDict

from django.db.models import Case, Exists, OuterRef, Prefetch, Sum, When
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categoria, PrecioEscalonado, Producto, ValorAtributo
from .serializers import ProductoListSerializer

DEFAULT_LIMIT = 8
MAX_LIMIT = 20


# ──────────── Helpers ────────────

def _optimizar_queryset_lista(qs):
    """Aplica los prefetch / annotate que requiere ProductoListSerializer."""
    return qs.only(
        'id', 'nombre', 'slug', 'precio_normal', 'precio_rebajado',
        'miniatura', 'imagen_principal', 'descripcion_corta', 'stock',
        'estado_inventario', 'rating_promedio', 'total_resenas',
    ).prefetch_related(
        Prefetch(
            'atributos',
            queryset=ValorAtributo.objects.select_related('atributo').filter(
                atributo__nombre__iexact='color'
            ),
            to_attr='color_atributos',
        ),
    ).annotate(
        has_tier=Exists(PrecioEscalonado.objects.filter(producto=OuterRef('pk'))),
    )


def _hidratar_productos(ids, request):
    """Carga los productos visibles preservando el orden de `ids`.

    Devuelve la lista serializada con `ProductoListSerializer`.
    """
    if not ids:
        return []

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    qs = (
        _optimizar_queryset_lista(
            Producto.objects.filter(
                pk__in=ids,
                visibilidad=True,
                estado='publicado',
            )
        )
        .order_by(preserved)
    )
    return ProductoListSerializer(qs, many=True, context={'request': request}).data


def _ids_por_co_ocurrencia(origen_ids, fuentes, exclude_ids, limit):
    """Suma scores por destino para los origen_ids dados, en orden de prioridad
    de fuentes. Devuelve una lista de IDs únicos limitada a `limit`.
    """
    from tracking.models import CoOcurrenciaProducto

    if not origen_ids:
        return []
    excluir = set(exclude_ids or []) | set(origen_ids)

    resultados = []
    vistos = set(excluir)

    for fuente in fuentes:
        if len(resultados) >= limit:
            break
        faltan = limit - len(resultados)
        rel = (
            CoOcurrenciaProducto.objects
            .filter(
                origen_id__in=origen_ids,
                fuente=fuente,
                destino__visibilidad=True,
                destino__estado='publicado',
            )
            .exclude(destino_id__in=vistos)
            .values('destino_id')
            .annotate(total=Sum('score'))
            .order_by('-total')[:faltan * 3]  # margen para filtrar duplicados
        )
        for r in rel:
            did = r['destino_id']
            if did in vistos:
                continue
            resultados.append(did)
            vistos.add(did)
            if len(resultados) >= limit:
                break

    return resultados


def _ids_misma_categoria(producto, exclude_ids, limit):
    """Productos de las mismas categorías del producto base."""
    cat_ids = list(producto.categorias.values_list('id', flat=True))
    if not cat_ids:
        return []
    qs = (
        Producto.objects
        .filter(
            categorias__in=cat_ids,
            visibilidad=True,
            estado='publicado',
            stock__gt=0,
        )
        .exclude(pk__in=exclude_ids)
        .order_by('-rating_promedio', '-fecha_creacion')
        .distinct()
        .values_list('id', flat=True)[:limit]
    )
    return list(qs)


def _ids_por_categorias(cat_ids, exclude_ids, limit):
    if not cat_ids:
        return []
    qs = (
        Producto.objects
        .filter(
            categorias__in=cat_ids,
            visibilidad=True,
            estado='publicado',
            stock__gt=0,
        )
        .exclude(pk__in=exclude_ids)
        .order_by('-rating_promedio', '-fecha_creacion')
        .distinct()
        .values_list('id', flat=True)[:limit]
    )
    return list(qs)


def _ids_destacados(exclude_ids, limit):
    from .services import get_destacados
    destacados = get_destacados(limite=limit + len(exclude_ids))
    out = []
    excl = set(exclude_ids)
    for d in destacados:
        if d.producto_id in excl:
            continue
        out.append(d.producto_id)
        if len(out) >= limit:
            break
    return out


def _ids_populares_recientes(exclude_ids, limit):
    """Top productos por views/add_carts en los últimos 30 días si hay datos.

    Si no hay agregados, cae a productos recientes en stock.
    """
    try:
        from tracking.models import AgregadoDiarioProducto
        from datetime import timedelta
        from django.utils import timezone

        desde = timezone.localtime().date() - timedelta(days=30)
        agg = (
            AgregadoDiarioProducto.objects
            .filter(fecha__gte=desde)
            .values('producto_id')
            .annotate(total=Sum('add_carts') + Sum('purchases') * 3)
            .order_by('-total')[:limit + len(exclude_ids)]
        )
        out = []
        excl = set(exclude_ids)
        for row in agg:
            pid = row['producto_id']
            if pid in excl:
                continue
            out.append(pid)
            if len(out) >= limit:
                break
        if out:
            return out
    except Exception:
        pass

    # Fallback total: recientes en stock
    qs = (
        Producto.objects
        .filter(visibilidad=True, estado='publicado', stock__gt=0)
        .exclude(pk__in=exclude_ids)
        .order_by('-fecha_creacion')
        .values_list('id', flat=True)[:limit]
    )
    return list(qs)


def _completar_hasta(ids, limit, *callbacks):
    """Aplica callbacks (que devuelven listas de IDs) hasta llenar `limit`."""
    seen = list(OrderedDict.fromkeys(ids))
    for cb in callbacks:
        if len(seen) >= limit:
            break
        faltan = limit - len(seen)
        nuevos = cb(seen, faltan)
        for nid in nuevos:
            if nid in seen:
                continue
            seen.append(nid)
            if len(seen) >= limit:
                break
    return seen[:limit]


# ──────────── Vistas ────────────

class RecomendacionesProductoAPIView(APIView):
    """GET /api/productos/<producto_id>/recomendaciones/?limit=8

    Recomendaciones para la PDP. Prioridad:
        1) co_purchase  2) co_cart  3) co_view
        4) misma categoría  5) destacados
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, producto_id):
        try:
            limit = max(1, min(int(request.query_params.get('limit', DEFAULT_LIMIT)), MAX_LIMIT))
        except (TypeError, ValueError):
            limit = DEFAULT_LIMIT

        try:
            producto = (
                Producto.objects
                .prefetch_related('categorias')
                .get(pk=producto_id, visibilidad=True, estado='publicado')
            )
        except Producto.DoesNotExist:
            return Response([])

        excl = [producto.id]

        # 1) Co-ocurrencia, en orden de prioridad
        ids = _ids_por_co_ocurrencia(
            origen_ids=[producto.id],
            fuentes=['co_purchase', 'co_cart', 'co_view'],
            exclude_ids=excl,
            limit=limit,
        )

        # 2/3) Fallbacks
        ids = _completar_hasta(
            ids, limit,
            lambda seen, n: _ids_misma_categoria(producto, seen, n),
            lambda seen, n: _ids_destacados(seen, n),
            lambda seen, n: _ids_populares_recientes(seen, n),
        )

        return Response(_hidratar_productos(ids, request))


class RecomendacionesHomeAPIView(APIView):
    """GET /api/recomendaciones/home/?limit=12

    Recomendaciones para el home, personalizadas si hay datos del usuario o
    visitor; si no, fallback a destacados / populares.

    Fuentes en orden:
        1) Eventos del usuario logueado (últimos 30 días) → co-ocurrencia
        2) Eventos del visitor anónimo (header X-Visitor-Id) → co-ocurrencia
        3) IDs enviados por el cliente (?recientes=1,2,3) → co-ocurrencia
        4) Categorías sugeridas por el cliente (?categorias=4,5,6)
        5) Destacados
        6) Populares recientes
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            limit = max(1, min(int(request.query_params.get('limit', 12)), MAX_LIMIT))
        except (TypeError, ValueError):
            limit = 12

        excl_ids = self._parse_ids(request.query_params.get('exclude'))
        recientes_cliente = self._parse_ids(request.query_params.get('recientes'))
        categorias_cliente = self._parse_ids(request.query_params.get('categorias'))

        # Origenes: ids de productos con los que el usuario ha interactuado
        origen_ids = self._origen_ids(request, recientes_cliente)

        ids = []
        if origen_ids:
            ids = _ids_por_co_ocurrencia(
                origen_ids=origen_ids,
                fuentes=['co_purchase', 'co_cart', 'co_view'],
                exclude_ids=set(origen_ids) | set(excl_ids),
                limit=limit,
            )

        ids = _completar_hasta(
            ids, limit,
            lambda seen, n: _ids_por_categorias(
                self._categorias_origen(origen_ids, categorias_cliente),
                set(seen) | set(origen_ids) | set(excl_ids),
                n,
            ),
            lambda seen, n: _ids_destacados(set(seen) | set(excl_ids), n),
            lambda seen, n: _ids_populares_recientes(set(seen) | set(excl_ids), n),
        )

        return Response(_hidratar_productos(ids, request))

    # ── helpers internos ──

    @staticmethod
    def _parse_ids(raw):
        if not raw:
            return []
        out = []
        for token in raw.split(','):
            token = token.strip()
            if not token:
                continue
            try:
                out.append(int(token))
            except ValueError:
                continue
        return out[:50]

    @staticmethod
    def _origen_ids(request, recientes_cliente):
        """Reconstruye los productos con los que el usuario ha interactuado.

        Se busca en `tracking.EventoUsuario` últimos 30 días, eventos
        view/add_cart/wishlist_add/purchase. Si no hay eventos en backend,
        se usan los `recientes_cliente` enviados por el frontend.
        """
        try:
            from datetime import timedelta

            from django.utils import timezone

            from tracking.models import (
                TIPO_ADD_CART,
                TIPO_PURCHASE,
                TIPO_VIEW,
                TIPO_WISHLIST_ADD,
                EventoUsuario,
            )

            desde = timezone.now() - timedelta(days=30)
            qs = EventoUsuario.objects.filter(
                created_at__gte=desde,
                producto__isnull=False,
                tipo__in=[TIPO_VIEW, TIPO_ADD_CART, TIPO_WISHLIST_ADD, TIPO_PURCHASE],
            )
            if request.user.is_authenticated:
                qs = qs.filter(usuario=request.user)
            else:
                vid = (request.headers.get('X-Visitor-Id') or '')[:64]
                if vid:
                    qs = qs.filter(visitor_id=vid)
                else:
                    qs = qs.none()

            ids = list(
                qs.order_by('-created_at')
                .values_list('producto_id', flat=True)
                .distinct()[:20]
            )
            if ids:
                return ids
        except Exception:
            pass

        return list(dict.fromkeys(recientes_cliente))[:20]

    @staticmethod
    def _categorias_origen(origen_ids, categorias_cliente):
        """Si tenemos productos de origen, sacamos sus categorías. Si no,
        usamos las categorías que el cliente nos envíe (historial local)."""
        if origen_ids:
            cat_ids = list(
                Categoria.objects
                .filter(productos__id__in=origen_ids)
                .values_list('id', flat=True)
                .distinct()
            )
            if cat_ids:
                return cat_ids
        return list(dict.fromkeys(categorias_cliente))
