import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
app = Celery('tienda')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# cada 15 min: sync completo
app.conf.beat_schedule = {
    "sync-supermex-15min": {
        "task": "suppliers.tasks.sync_supermex_full",
        "schedule": crontab(minute="*/15"),
    },
}
