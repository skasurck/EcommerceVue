from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Direccion, MetodoEnvio, Pedido, PedidoItem, PedidoHistorial
from carrito.models import CartItem
from productos.models import Producto


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        exclude = ('user',)

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        direccion = Direccion.objects.create(user=user, **validated_data)
        self._set_default(user, direccion, validated_data.get('predeterminada'))
        self._populate_profile(user, direccion)
        return direccion

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance = super().update(instance, validated_data)
        if validated_data.get('predeterminada'):
            self._set_default(user, instance, True)
        elif not Direccion.objects.filter(user=user, predeterminada=True).exists():
            self._set_default(user, instance, True)
        return instance

    def _set_default(self, user, direccion, set_default):
        has_default = Direccion.objects.filter(user=user, predeterminada=True).exclude(pk=direccion.pk).exists()
        if set_default or not has_default:
            Direccion.objects.filter(user=user).exclude(pk=direccion.pk).update(predeterminada=False)
            direccion.predeterminada = True
            direccion.save(update_fields=['predeterminada'])

    def _populate_profile(self, user, direccion):
        perfil = getattr(user, 'perfil', None)
        updated_user = []
        if not user.first_name:
            user.first_name = direccion.nombre
            updated_user.append('first_name')
        if not user.last_name:
            user.last_name = direccion.apellidos
            updated_user.append('last_name')
        if updated_user:
            user.save(update_fields=updated_user)
        if perfil and not perfil.empresa:
            perfil.empresa = direccion.nombre_empresa
            perfil.save(update_fields=['empresa'])


class MetodoEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoEnvio
        fields = ['id', 'nombre', 'costo', 'descripcion']


class PedidoItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = PedidoItem
        fields = ['producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']


class PedidoHistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoHistorial
        fields = ['fecha', 'descripcion']


class PedidoSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()
    items = PedidoItemSerializer(many=True, write_only=True, required=False)
    detalles = PedidoItemSerializer(source='items', many=True, read_only=True)
    datos_pago = serializers.JSONField(required=False)
    save_address = serializers.BooleanField(write_only=True, required=False, default=False)
    metodo_envio_detalle = MetodoEnvioSerializer(source='metodo_envio', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    historial = PedidoHistorialSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'direccion', 'metodo_envio', 'metodo_envio_detalle', 'metodo_pago',
                  'metodo_pago_display', 'indicaciones', 'subtotal', 'costo_envio', 'total',
                  'datos_pago', 'items', 'detalles', 'save_address', 'estado', 'historial',
                  'creado']
        read_only_fields = ['id', 'creado', 'subtotal', 'costo_envio', 'total', 'detalles',
                            'historial', 'metodo_envio_detalle', 'metodo_pago_display']
        extra_kwargs = {'estado': {'required': False}}

    def create(self, validated_data):
        request = self.context.get('request')
        direccion_data = validated_data.pop('direccion')
        items_data = validated_data.pop('items', None)
        save_address = validated_data.pop('save_address', False)
        validated_data.pop('user', None)
        user = request.user if request and request.user.is_authenticated else None

        items_from_cart = items_data is None
        if items_from_cart:
            if user:
                cart_items = CartItem.objects.filter(user=user)
                if not cart_items.exists():
                    raise ValidationError('El carrito está vacío')
                items_data = [{'producto': ci.producto, 'cantidad': ci.cantidad} for ci in cart_items]
            else:
                raise ValidationError('No hay productos para el pedido')

        metodo_envio = validated_data['metodo_envio']
        with transaction.atomic():
            direccion_data.pop('user', None)
            direccion = Direccion.objects.create(
                user=user if save_address else None, **direccion_data
            )
            if save_address and user:
                has_default = Direccion.objects.filter(user=user, predeterminada=True).exclude(pk=direccion.pk).exists()
                if not has_default:
                    Direccion.objects.filter(user=user).exclude(pk=direccion.pk).update(predeterminada=False)
                    direccion.predeterminada = True
                    direccion.save(update_fields=['predeterminada'])

                perfil = getattr(user, 'perfil', None)
                updated_user = []
                if not user.first_name:
                    user.first_name = direccion.nombre
                    updated_user.append('first_name')
                if not user.last_name:
                    user.last_name = direccion.apellidos
                    updated_user.append('last_name')
                if updated_user:
                    user.save(update_fields=updated_user)
                if perfil and not perfil.empresa:
                    perfil.empresa = direccion.nombre_empresa
                    perfil.save(update_fields=['empresa'])
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
                if not items_from_cart and producto.stock < cantidad:
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
                if not items_from_cart:
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
