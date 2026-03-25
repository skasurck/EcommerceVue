from django.db import models
from django.contrib.auth.models import User

from carrito.models import Cart
from promotions.models import Cupon


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
    predeterminada = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}, {self.calle} {self.numero_exterior}"


class MetodoEnvio(models.Model):
    nombre = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True)
    #tiempo_entrega = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nombre


METODO_PAGO_CHOICES = (
    ('transferencia', 'Transferencia directa'),
    ('tarjeta', 'Tarjeta'),
    ('mercadopago', 'Mercado Pago'),
)


class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    metodo_envio = models.ForeignKey(MetodoEnvio, on_delete=models.PROTECT)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    indicaciones = models.TextField(blank=True)
    cupon = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    datos_pago = models.JSONField(blank=True, default=dict)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('pagado', 'Pagado'),
            ('confirmado', 'Confirmado'),
            ('enviado', 'Enviado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente',
    )
    stock_restaurado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    papelera = models.BooleanField(default=False)
    eliminado_en = models.DateTimeField(null=True, blank=True)

    # Envío
    numero_guia = models.CharField(max_length=200, blank=True, default='')

    # Mercado Pago
    mercadopago_preference_id = models.CharField(max_length=100, blank=True, null=True)
    mercadopago_payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        estado_anterior = None
        if self.pk:
            try:
                estado_anterior = Pedido.objects.get(pk=self.pk).estado
            except Pedido.DoesNotExist:
                pass
        super().save(*args, **kwargs)

        if (
            self.estado == 'cancelado'
            and estado_anterior in ['pagado', 'confirmado']
            and not self.stock_restaurado
        ):
            for item in self.items.all():
                producto = item.producto
                producto.stock += item.cantidad
                producto.save(update_fields=['stock'])
            self.stock_restaurado = True
            super().save(update_fields=['stock_restaurado'])
            PedidoHistorial.objects.create(
                pedido=self,
                descripcion='Stock devuelto por cancelación',
            )

        # ── Emails transaccionales ─────────────────────────────────────────
        try:
            from pedidos.emails import (
                enviar_email_pedido_creado,
                enviar_email_pago_confirmado,
                enviar_email_enviado,
                enviar_email_cancelado,
            )
            if is_new:
                enviar_email_pedido_creado.delay(self.pk)
            elif estado_anterior and estado_anterior != self.estado:
                if self.estado == 'pagado':
                    enviar_email_pago_confirmado.delay(self.pk)
                elif self.estado == 'enviado':
                    enviar_email_enviado.delay(self.pk)
                elif self.estado == 'cancelado':
                    enviar_email_cancelado.delay(self.pk)
        except Exception:
            pass  # no bloquear el guardado si el email falla


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class PedidoHistorial(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='historial', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} - {self.descripcion}"
