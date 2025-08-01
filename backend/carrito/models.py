from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"