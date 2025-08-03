from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from productos.models import Producto

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class CartReservation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart_reservation')
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Reserva de {self.user.username} hasta {self.expires_at}"

    def refresh_expiration(self):
        """Reinicia el temporizador 40 min sin exceder 3 horas desde el inicio."""
        now = timezone.now()
        if self.expires_at < now:
            self.started_at = now
        max_end = self.started_at + timedelta(hours=3)
        self.expires_at = min(max_end, now + timedelta(minutes=40))
        self.save()

