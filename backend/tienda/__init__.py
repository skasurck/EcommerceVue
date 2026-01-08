from .celery import app as celery_app

__all__ = ('celery_app',)

# esto es para que se reconozca el módulo celery al iniciar Django
# y al poner import tienda.celery.* solo se importe celery_app