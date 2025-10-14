from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from productos.models import Producto


class Cart(models.Model):
    """Carrito de compras que puede pertenecer a un usuario o a una sesión anónima."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        return f"Carrito invitado #{self.pk}"

    @property
    def is_guest(self):
        return self.user_id is None


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "producto")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def user(self):
        return self.cart.user


class CartReservation(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name="reservation")
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def __str__(self):
        owner = self.cart.user.username if self.cart.user else f"invitado #{self.cart_id}"
        return f"Reserva de {owner} hasta {self.expires_at}"

    def refresh_expiration(self):
        """Reinicia el temporizador 40 min sin exceder 3 horas desde el inicio."""
        now = timezone.now()
        if self.expires_at < now:
            self.started_at = now
        max_end = self.started_at + timedelta(hours=3)
        self.expires_at = min(max_end, now + timedelta(minutes=40))
        self.save()
