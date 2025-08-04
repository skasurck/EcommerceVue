from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Direccion, MetodoEnvio, Pedido, PedidoItem
from carrito.models import CartItem
from productos.models import Producto


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        exclude = ('user',)


class MetodoEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoEnvio
        fields = ['id', 'nombre', 'costo']


class PedidoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoItem
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()
    items = PedidoItemSerializer(many=True, write_only=True, required=False)
    detalles = PedidoItemSerializer(source='items', many=True, read_only=True)
    datos_pago = serializers.JSONField(required=False)
    save_address = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Pedido
        fields = ['id', 'direccion', 'metodo_envio', 'metodo_pago', 'indicaciones',
                  'subtotal', 'costo_envio', 'total', 'datos_pago', 'items', 'detalles', 'save_address', 'creado']
        read_only_fields = ['id', 'creado', 'subtotal', 'costo_envio', 'total', 'detalles']

    def create(self, validated_data):
        request = self.context.get('request')
        direccion_data = validated_data.pop('direccion')
        items_data = validated_data.pop('items', None)
        save_address = validated_data.pop('save_address', False)
        user = request.user if request and request.user.is_authenticated else None

        if items_data is None:
            if user:
                cart_items = CartItem.objects.filter(user=user)
                if not cart_items.exists():
                    raise ValidationError('El carrito está vacío')
                items_data = [{'producto': ci.producto, 'cantidad': ci.cantidad} for ci in cart_items]
            else:
                raise ValidationError('No hay productos para el pedido')

        metodo_envio = validated_data['metodo_envio']
        with transaction.atomic():
            direccion = Direccion.objects.create(
                user=user if save_address else None, **direccion_data
            )
            pedido = Pedido.objects.create(user=user, direccion=direccion, **validated_data)

            subtotal = Decimal('0')
            for item in items_data:
                producto_id = (
                    item['producto'].id
                    if isinstance(item['producto'], Producto)
                    else item['producto']
                )
                producto = Producto.objects.select_for_update().get(pk=producto_id)
                cantidad = item['cantidad']
                if producto.stock < cantidad:
                    raise ValidationError(f'Stock insuficiente para {producto.nombre}')

                precio = producto.precio_rebajado or producto.precio_normal
                tiers = producto.precios_escalonados.all()
                for tier in tiers:
                    if cantidad >= tier.cantidad_minima and tier.precio_unitario < precio:
                        precio = tier.precio_unitario
                item_subtotal = precio * cantidad
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=item_subtotal,
                )
                producto.stock -= cantidad
                producto.save(update_fields=['stock'])
                subtotal += item_subtotal

            pedido.subtotal = subtotal
            pedido.costo_envio = metodo_envio.costo
            pedido.total = subtotal + metodo_envio.costo
            pedido.save(update_fields=['subtotal', 'costo_envio', 'total'])

            if user:
                CartItem.objects.filter(user=user).delete()

            return pedido
