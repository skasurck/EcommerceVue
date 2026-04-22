import logging

from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import TIPO_PURCHASE, EventoUsuario

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def fusionar_tracking_al_login(sender, request, user, **kwargs):
    """Asocia eventos anónimos del visitor al usuario al iniciar sesión."""
    if not request:
        return
    visitor_id = ''
    try:
        visitor_id = request.headers.get('X-Visitor-Id', '') or ''
    except Exception:
        pass
    if not visitor_id:
        visitor_id = request.COOKIES.get('mk_vid', '') or ''
    if not visitor_id:
        return

    try:
        EventoUsuario.objects.filter(
            visitor_id=visitor_id[:64],
            usuario__isnull=True,
        ).update(usuario=user)
    except Exception as exc:  # pragma: no cover
        logger.warning("tracking: no se pudo fusionar visitor->user (%s)", exc)


@receiver(pre_save, sender='pedidos.Pedido')
def track_purchase_on_pedido(sender, instance, **kwargs):
    """Crea eventos `purchase` cuando un Pedido pasa a estado 'pagado'."""
    if not instance.pk:
        return
    try:
        anterior = sender.objects.only('estado').get(pk=instance.pk).estado
    except sender.DoesNotExist:
        return

    if anterior == 'pagado' or instance.estado != 'pagado':
        return

    def _crear_eventos():
        try:
            items = list(instance.items.select_related('producto').all())
        except Exception:
            return
        if not items:
            return
        eventos = [
            EventoUsuario(
                usuario=instance.user,
                tipo=TIPO_PURCHASE,
                producto=item.producto,
                metadata={
                    'pedido_id': instance.pk,
                    'cantidad': item.cantidad,
                    'precio': str(item.precio_unitario),
                },
            )
            for item in items
        ]
        EventoUsuario.objects.bulk_create(eventos, ignore_conflicts=True)

    transaction.on_commit(_crear_eventos)
