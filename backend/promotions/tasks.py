from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task(name='promotions.create_daily_offers')
def create_daily_offers():
    """Rota las ofertas diarias: desactiva las actuales y crea 10 nuevas."""
    logger.info('Iniciando rotación de ofertas diarias...')
    call_command('create_daily_offers')
    logger.info('Rotación de ofertas diarias completada.')
