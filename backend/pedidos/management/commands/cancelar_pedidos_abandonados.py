from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pedidos.models import Pedido


class Command(BaseCommand):
    help = 'Cancela pedidos de Mercado Pago pendientes por más de 2 horas (abandonados)'

    def handle(self, *args, **options):
        limite = timezone.now() - timedelta(hours=2)
        qs = Pedido.objects.filter(
            metodo_pago='mercadopago',
            estado='pendiente',
            fecha_creacion__lt=limite,
        )
        total = qs.count()
        qs.update(estado='cancelado')
        self.stdout.write(self.style.SUCCESS(f'Pedidos abandonados cancelados: {total}'))
