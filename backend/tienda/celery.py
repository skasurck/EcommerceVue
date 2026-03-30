import os
import multiprocessing

# Desactivar el paralelismo de los tokenizers de Hugging Face para evitar deadlocks en Celery.
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from celery import Celery
from celery.schedules import crontab

# Forzar el método de inicio 'spawn' para compatibilidad con CUDA en procesos fork
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    # set_start_method solo se puede llamar una vez. Si ya está configurado,
    # es probable que esté bien.
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
app = Celery('tienda')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()                          # busca tasks.py en cada app
app.autodiscover_tasks(related_name='emails')     # busca emails.py en cada app

app.conf.beat_schedule = {
    "sync-supermex-diario-3am": {
        "task": "suppliers.tasks.sync_supermex_full",
        "schedule": crontab(hour=3, minute=0),
    },
    "recalcular-destacados-cada-hora": {
        "task": "productos.recalcular_destacados",
        "schedule": crontab(minute=0),  # cada hora en punto
    },
    "cancelar-pedidos-mp-abandonados": {
        "task": "pedidos.cancelar_pedidos_mp_abandonados",
        "schedule": crontab(minute=0, hour="*/2"),  # cada 2 horas
    },
    "rotar-ofertas-diarias": {
        "task": "promotions.create_daily_offers",
        "schedule": crontab(minute=0, hour=0),  # cada día a medianoche
    },
}
