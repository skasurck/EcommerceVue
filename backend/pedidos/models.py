from django.db import models
from django.contrib.auth.models import User


class Direccion(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='direcciones')
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    nombre_empresa = models.CharField(max_length=150, blank=True)
    calle = models.CharField(max_length=150)
    numero_exterior = models.CharField(max_length=50)
    numero_interior = models.CharField(max_length=50, blank=True)
    colonia = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=150)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    referencias = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}, {self.calle} {self.numero_exterior}"


class MetodoEnvio(models.Model):
    nombre = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


METODO_PAGO_CHOICES = (
    ('transferencia', 'Transferencia directa'),
    ('tarjeta', 'Tarjeta'),
)


class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    metodo_envio = models.ForeignKey(MetodoEnvio, on_delete=models.PROTECT)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    indicaciones = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    datos_pago = models.JSONField(blank=True, default=dict)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
