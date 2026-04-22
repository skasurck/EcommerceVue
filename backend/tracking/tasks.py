import json
import logging
from collections import defaultdict
from datetime import timedelta

import redis
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    FUENTE_CO_CART,
    FUENTE_CO_PURCHASE,
    FUENTE_CO_VIEW,
    TIPO_ADD_CART,
    TIPO_CLICK_REC,
    TIPO_IMPRESSION_REC,
    TIPO_PURCHASE,
    TIPO_VIEW,
    TIPO_WISHLIST_ADD,
    AgregadoDiarioProducto,
    CoOcurrenciaProducto,
    EventoUsuario,
)

logger = logging.getLogger(__name__)

REDIS_QUEUE_URL = getattr(
    settings, 'TRACKING_REDIS_URL', 'redis://127.0.0.1:6379/2'
)
REDIS_QUEUE_KEY = 'tracking:eventos'

_redis_client = None


def _redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_QUEUE_URL, decode_responses=True)
    return _redis_client


@shared_task(name='tracking.drenar_cola_eventos')
def drenar_cola_eventos(max_items: int = 2000) -> int:
    """Saca eventos de la cola Redis y los inserta en bulk."""
    try:
        client = _redis()
        pipe = client.pipeline()
        for _ in range(max_items):
            pipe.rpop(REDIS_QUEUE_KEY)
        raw = [x for x in pipe.execute() if x]
    except redis.RedisError as exc:
        logger.warning("tracking: redis no disponible (%s)", exc)
        return 0

    if not raw:
        return 0

    objetos = []
    for item in raw:
        try:
            d = json.loads(item)
        except (TypeError, json.JSONDecodeError):
            continue
        tipo = d.get('tipo')
        if not tipo:
            continue
        objetos.append(EventoUsuario(
            usuario_id=d.get('usuario_id'),
            session_key=(d.get('session_key') or '')[:64],
            visitor_id=(d.get('visitor_id') or '')[:64],
            tipo=tipo,
            producto_id=d.get('producto_id') or None,
            categoria_id=d.get('categoria_id') or None,
            metadata=d.get('metadata') or {},
            ip_hash=(d.get('ip_hash') or '')[:64],
            user_agent=(d.get('user_agent') or '')[:255],
        ))

    if not objetos:
        return 0

    EventoUsuario.objects.bulk_create(objetos, batch_size=500, ignore_conflicts=True)
    return len(objetos)


@shared_task(name='tracking.actualizar_agregado_diario')
def actualizar_agregado_diario(dias: int = 2) -> int:
    """Refresca AgregadoDiarioProducto para los últimos `dias` días."""
    desde = timezone.now() - timedelta(days=dias)
    eventos = (
        EventoUsuario.objects
        .filter(created_at__gte=desde, producto__isnull=False, is_bot=False)
        .values_list('producto_id', 'tipo', 'created_at')
    )

    contador = defaultdict(lambda: defaultdict(int))
    for prod_id, tipo, created in eventos:
        fecha = timezone.localtime(created).date()
        contador[(prod_id, fecha)][tipo] += 1

    objetos = []
    for (prod_id, fecha), counts in contador.items():
        objetos.append(AgregadoDiarioProducto(
            producto_id=prod_id,
            fecha=fecha,
            views=counts.get(TIPO_VIEW, 0),
            add_carts=counts.get(TIPO_ADD_CART, 0),
            wishlist_adds=counts.get(TIPO_WISHLIST_ADD, 0),
            purchases=counts.get(TIPO_PURCHASE, 0),
            impressions_rec=counts.get(TIPO_IMPRESSION_REC, 0),
            clicks_rec=counts.get(TIPO_CLICK_REC, 0),
        ))

    fechas = {fecha for (_, fecha), _ in contador.items()}
    with transaction.atomic():
        if fechas:
            AgregadoDiarioProducto.objects.filter(fecha__in=fechas).delete()
        AgregadoDiarioProducto.objects.bulk_create(objetos, batch_size=500)

    return len(objetos)


@shared_task(name='tracking.recalcular_co_ocurrencia')
def recalcular_co_ocurrencia(dias: int = 30, max_top: int = 15) -> dict:
    """Calcula co_view, co_cart y co_purchase a partir de EventoUsuario.

    Estrategia: agrupa por visitor_id (o usuario_id si está) y por tipo, luego cuenta
    pares de productos co-ocurrentes en la misma sesión.
    """
    desde = timezone.now() - timedelta(days=dias)
    eventos = (
        EventoUsuario.objects
        .filter(
            created_at__gte=desde,
            is_bot=False,
            producto__isnull=False,
            tipo__in=[TIPO_VIEW, TIPO_ADD_CART, TIPO_PURCHASE],
        )
        .values_list('usuario_id', 'visitor_id', 'producto_id', 'tipo')
    )

    sesiones = defaultdict(lambda: {
        TIPO_VIEW: set(),
        TIPO_ADD_CART: set(),
        TIPO_PURCHASE: set(),
    })
    for uid, vid, pid, tipo in eventos:
        clave = f"u:{uid}" if uid else (f"v:{vid}" if vid else None)
        if not clave:
            continue
        sesiones[clave][tipo].add(pid)

    resumen = {}

    def acumular(fuente: str, clave_tipo: str, umbral: int):
        co = defaultdict(lambda: defaultdict(int))
        for s in sesiones.values():
            prods = list(s[clave_tipo])
            n = len(prods)
            if n < 2:
                continue
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = prods[i], prods[j]
                    co[a][b] += 1
                    co[b][a] += 1

        bulk = []
        for origen, vecinos in co.items():
            top = sorted(vecinos.items(), key=lambda x: -x[1])[:max_top]
            for destino, score in top:
                if score >= umbral:
                    bulk.append(CoOcurrenciaProducto(
                        origen_id=origen,
                        destino_id=destino,
                        fuente=fuente,
                        score=float(score),
                    ))

        with transaction.atomic():
            CoOcurrenciaProducto.objects.filter(fuente=fuente).delete()
            CoOcurrenciaProducto.objects.bulk_create(
                bulk, batch_size=2000, ignore_conflicts=True,
            )
        resumen[fuente] = len(bulk)

    acumular(FUENTE_CO_VIEW, TIPO_VIEW, umbral=3)
    acumular(FUENTE_CO_CART, TIPO_ADD_CART, umbral=2)
    acumular(FUENTE_CO_PURCHASE, TIPO_PURCHASE, umbral=2)

    return resumen


@shared_task(name='tracking.purgar_eventos_antiguos')
def purgar_eventos_antiguos(dias: int = 540) -> int:
    """Borra eventos con más de `dias` días (default 18 meses)."""
    limite = timezone.now() - timedelta(days=dias)
    deleted, _ = EventoUsuario.objects.filter(created_at__lt=limite).delete()
    return deleted
