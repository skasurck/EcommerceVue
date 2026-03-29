"""
Management command para generar keywords de búsqueda en productos existentes.

Uso:
  # Solo productos sin keywords (recomendado primera vez)
  python manage.py generate_keywords

  # Forzar regeneración en TODOS los productos
  python manage.py generate_keywords --all

  # Solo un producto específico
  python manage.py generate_keywords --id 42
"""
import time

from django.core.management.base import BaseCommand

from productos.models import Producto
from productos.tasks import generate_keywords_task


class Command(BaseCommand):
    help = 'Genera keywords de búsqueda con IA para productos existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar keywords incluso en productos que ya las tienen',
        )
        parser.add_argument(
            '--id',
            type=int,
            dest='product_id',
            help='Generar keywords solo para el producto con este ID',
        )

    def handle(self, *args, **options):
        if options['product_id']:
            qs = Producto.objects.filter(pk=options['product_id'])
        elif options['all']:
            qs = Producto.objects.all()
        else:
            qs = Producto.objects.filter(search_keywords='')

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING(
                'No hay productos que necesiten keywords. '
                'Usa --all para forzar regeneración.'
            ))
            return

        self.stdout.write(f'Encolando {total} productos en Celery...')
        for i, product in enumerate(qs.only('pk', 'nombre'), 1):
            generate_keywords_task.delay(product.pk)
            self.stdout.write(f'  [{i}/{total}] {product.nombre[:60]}')
            # Pausa mínima para no saturar la cola
            if i % 50 == 0:
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ {total} tareas encoladas. '
            'Celery las procesará en background con ~0.5s entre cada una.'
        ))
