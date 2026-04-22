import hashlib
import json
import re

import redis
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import (
    TIPOS_VALIDOS,
    ConsentimientoTracking,
    EventoUsuario,
)

REDIS_QUEUE_URL = getattr(
    settings, 'TRACKING_REDIS_URL', 'redis://127.0.0.1:6379/2'
)
REDIS_QUEUE_KEY = 'tracking:eventos'
REDIS_QUEUE_HARD_CAP = 200_000

_redis_client = None


def _redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_QUEUE_URL, decode_responses=True)
    return _redis_client


BOT_UA_RE = re.compile(
    r'bot|crawler|spider|headless|preview|facebookexternalhit|slack|discord',
    re.IGNORECASE,
)
MAX_BATCH = 50


def _hash_ip(ip: str) -> str:
    if not ip:
        return ''
    salt = settings.SECRET_KEY
    return hashlib.sha256((ip + salt).encode('utf-8')).hexdigest()[:32]


def _client_ip(request) -> str:
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or ''


class TrackingThrottle(AnonRateThrottle):
    scope = 'tracking'


class EventoTrackingAPIView(APIView):
    """POST /api/tracking/eventos/

    Body:
        {"eventos": [
            {"tipo": "view", "producto_id": 123, "metadata": {...}, "ts": 1700000000000},
            ...
        ]}
    """
    permission_classes = [AllowAny]
    throttle_classes = [TrackingThrottle, UserRateThrottle]
    authentication_classes = []  # JWT no es necesario; aceptamos anónimos

    def post(self, request):
        eventos = request.data.get('eventos')
        if not isinstance(eventos, list):
            return Response({'error': 'eventos debe ser lista'}, status=status.HTTP_400_BAD_REQUEST)
        if len(eventos) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        if len(eventos) > MAX_BATCH:
            eventos = eventos[:MAX_BATCH]

        ua = (request.headers.get('User-Agent') or '')[:255]
        if BOT_UA_RE.search(ua):
            return Response(status=status.HTTP_204_NO_CONTENT)

        if not request.session.session_key:
            try:
                request.session.create()
            except Exception:
                pass
        sess = request.session.session_key or ''
        visitor_id = (request.headers.get('X-Visitor-Id') or '')[:64]
        uid = request.user.id if request.user.is_authenticated else None
        ip_hash = _hash_ip(_client_ip(request))

        try:
            client = _redis()
            pipe = client.pipeline()
            encolados = 0
            for e in eventos:
                if not isinstance(e, dict):
                    continue
                tipo = e.get('tipo')
                if tipo not in TIPOS_VALIDOS:
                    continue
                payload = {
                    'usuario_id': uid,
                    'session_key': sess,
                    'visitor_id': visitor_id,
                    'tipo': tipo,
                    'producto_id': e.get('producto_id'),
                    'categoria_id': e.get('categoria_id'),
                    'metadata': e.get('metadata') or {},
                    'ip_hash': ip_hash,
                    'user_agent': ua,
                    'ts': e.get('ts'),
                }
                pipe.lpush(REDIS_QUEUE_KEY, json.dumps(payload))
                encolados += 1
            if encolados:
                pipe.ltrim(REDIS_QUEUE_KEY, 0, REDIS_QUEUE_HARD_CAP - 1)
                pipe.execute()
        except redis.RedisError:
            # Tracking no debe romper nunca el request
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ConsentimientoAPIView(APIView):
    """POST /api/tracking/consentimiento/

    Body: {"analytics": true, "personalizacion": true, "v": "v1"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        vid = (request.headers.get('X-Visitor-Id') or '')[:64]
        analytics = bool(request.data.get('analytics'))
        personalizacion = bool(request.data.get('personalizacion'))
        version = (request.data.get('v') or 'v1')[:20]
        ua = (request.headers.get('User-Agent') or '')[:255]
        ip_hash = _hash_ip(_client_ip(request))

        defaults = {
            'acepta_analytics': analytics,
            'acepta_personalizacion': personalizacion,
            'version_aviso': version,
            'user_agent': ua,
            'ip_hash': ip_hash,
        }

        if request.user.is_authenticated:
            ConsentimientoTracking.objects.update_or_create(
                usuario=request.user,
                defaults={**defaults, 'visitor_id': vid},
            )
        else:
            if not vid:
                return Response({'error': 'visitor_id requerido'}, status=400)
            ConsentimientoTracking.objects.update_or_create(
                visitor_id=vid, usuario=None,
                defaults=defaults,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MisDatosTrackingAPIView(APIView):
    """DELETE /api/tracking/mis-datos/

    Derechos ARCO (LFPDPPP): el usuario puede borrar todo su historial de tracking.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        EventoUsuario.objects.filter(usuario=request.user).delete()
        ConsentimientoTracking.objects.filter(usuario=request.user).update(
            acepta_analytics=False,
            acepta_personalizacion=False,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request):
        consent = ConsentimientoTracking.objects.filter(usuario=request.user).first()
        eventos_count = EventoUsuario.objects.filter(usuario=request.user).count()
        return Response({
            'eventos': eventos_count,
            'acepta_analytics': bool(consent and consent.acepta_analytics),
            'acepta_personalizacion': bool(consent and consent.acepta_personalizacion),
        })
