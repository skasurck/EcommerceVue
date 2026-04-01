import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name='pedidos.cancelar_pedidos_mp_abandonados')
def cancelar_pedidos_mp_abandonados():
    """
    Cancela pedidos de Mercado Pago que llevan más de 2 horas en estado
    'iniciado' o 'pendiente' sin completar el pago. Evita acumular pedidos fantasma.
    """
    from pedidos.models import Pedido

    limite = timezone.now() - timedelta(hours=2)
    abandonados = Pedido.objects.filter(
        metodo_pago='mercadopago',
        estado__in=['iniciado', 'pendiente'],
        creado__lt=limite,
    )
    total = abandonados.count()
    if total:
        abandonados.update(estado='cancelado')
        logger.info("Pedidos MP abandonados cancelados: %d", total)
    return total
