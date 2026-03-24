from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Direccion, MetodoEnvio, Pedido, PedidoItem, PedidoHistorial
from carrito.services import clear_cart, ensure_cart_for_request
from productos.models import Producto
from usuarios.models import Perfil


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
        perfil, _ = Perfil.objects.get_or_create(user=user)
        updated_user = []
        if not user.first_name:
            user.first_name = direccion.nombre
            updated_user.append('first_name')
        if not user.last_name:
            user.last_name = direccion.apellidos
            updated_user.append('last_name')
        if not user.email:
            user.email = direccion.email
            updated_user.append('email')
        if updated_user:
            user.save(update_fields=updated_user)
        updated_perfil = []
        if not perfil.telefono:
            perfil.telefono = direccion.telefono
            updated_perfil.append('telefono')
        if not perfil.empresa:
            perfil.empresa = direccion.nombre_empresa
            updated_perfil.append('empresa')
        if updated_perfil:
            perfil.save(update_fields=updated_perfil)


class MetodoEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoEnvio
        fields = ['id', 'nombre', 'costo', 'descripcion']


class PedidoItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_sku = serializers.CharField(source='producto.sku', read_only=True)
    producto_imagen = serializers.SerializerMethodField()

    def get_producto_imagen(self, obj):
        request = self.context.get('request')
        imagen = obj.producto.miniatura or obj.producto.imagen_principal
        if imagen:
            url = imagen.url
            return request.build_absolute_uri(url) if request else url
        return None

    class Meta:
        model = PedidoItem
        fields = ['producto', 'producto_nombre', 'producto_sku', 'producto_imagen', 'cantidad', 'precio_unitario', 'subtotal']
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
    cliente_nombre_completo = serializers.SerializerMethodField(read_only=True)
    direccion_resumen = serializers.SerializerMethodField(read_only=True)
    cart_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'direccion', 'metodo_envio', 'metodo_envio_detalle', 'metodo_pago',
                  'metodo_pago_display', 'indicaciones', 'subtotal', 'costo_envio', 'total',
                  'datos_pago', 'items', 'detalles', 'save_address', 'estado', 'numero_guia',
                  'historial', 'creado', 'papelera', 'cliente_nombre_completo',
                  'direccion_resumen', 'cart_id']
        read_only_fields = ['id', 'creado', 'subtotal', 'costo_envio', 'total', 'detalles',
                            'historial', 'metodo_envio_detalle', 'metodo_pago_display',
                            'papelera', 'cliente_nombre_completo', 'direccion_resumen',
                            'cart_id']
        extra_kwargs = {'estado': {'required': False}}

    def get_cliente_nombre_completo(self, obj):
        if obj.direccion:
            return f"{obj.direccion.nombre} {obj.direccion.apellidos}".strip()
        return ""

    def get_direccion_resumen(self, obj):
        if not obj.direccion:
            return ""
        d = obj.direccion
        partes = [
            f"Calle {d.calle} {d.numero_exterior}",
            d.colonia,
            d.ciudad,
            d.estado,
            d.codigo_postal,
        ]
        return ", ".join([p for p in partes if p])

    def get_cart_id(self, obj):
        return obj.cart_id

    def validate_datos_pago(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("datos_pago debe ser un objeto JSON.")
        allowed_keys = {'token', 'preference_id', 'payment_id', 'status', 'referencia', 'notas'}
        unknown = set(value.keys()) - allowed_keys
        if unknown:
            raise serializers.ValidationError(f"Claves no permitidas en datos_pago: {unknown}")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        direccion_data = validated_data.pop('direccion')
        items_data = validated_data.pop('items', None)
        save_address = validated_data.pop('save_address', False)
        validated_data.pop('user', None)
        user = request.user if request and request.user.is_authenticated else None

        cart = None
        items_from_cart = items_data is None
        if items_from_cart:
            if not request:
                raise ValidationError('No hay productos para el pedido')
            cart = ensure_cart_for_request(request)
            cart_items = cart.items.select_related('producto')
            if not cart_items.exists():
                raise ValidationError('El carrito está vacío')
            items_data = [
                {'producto': ci.producto, 'cantidad': ci.cantidad}
                for ci in cart_items
            ]

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

                perfil, _ = Perfil.objects.get_or_create(user=user)
                updated_user = []
                if not user.first_name:
                    user.first_name = direccion.nombre
                    updated_user.append('first_name')
                if not user.last_name:
                    user.last_name = direccion.apellidos
                    updated_user.append('last_name')
                if not user.email:
                    user.email = direccion.email
                    updated_user.append('email')
                if updated_user:
                    user.save(update_fields=updated_user)
                updated_perfil = []
                if not perfil.telefono:
                    perfil.telefono = direccion.telefono
                    updated_perfil.append('telefono')
                if not perfil.empresa:
                    perfil.empresa = direccion.nombre_empresa
                    updated_perfil.append('empresa')
                if updated_perfil:
                    perfil.save(update_fields=updated_perfil)
            pedido = Pedido.objects.create(
                user=user, cart=cart, direccion=direccion, **validated_data
            )

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

            if cart:
                clear_cart(cart)

            return pedido

    def update(self, instance, validated_data):
        direccion_data = validated_data.pop("direccion", None)
        items_data = validated_data.pop("items", None)

        if direccion_data:
            for attr, value in direccion_data.items():
                setattr(instance.direccion, attr, value)
            instance.direccion.save()

        if items_data is not None:
            instance.items.all().delete()
            subtotal = Decimal("0")
            for item in items_data:
                producto_id = (
                    item["producto"].id
                    if isinstance(item["producto"], Producto)
                    else item["producto"]
                )
                producto = Producto.objects.get(pk=producto_id)
                cantidad = item["cantidad"]
                precio = producto.precio_rebajado or producto.precio_normal
                item_subtotal = precio * cantidad
                PedidoItem.objects.create(
                    pedido=instance,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=item_subtotal,
                )
                subtotal += item_subtotal
            instance.subtotal = subtotal

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.total = instance.subtotal + instance.costo_envio
        instance.save()
        return instance
