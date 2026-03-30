from django.utils import timezone
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CartItem, CartReservation
from .serializers import CartItemSerializer
from .services import clear_cart, ensure_cart_for_request


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        cart = self._get_cart()
        self._clear_expired(cart)
        return cart.items.select_related("producto", "cart").order_by("id")

    def perform_create(self, serializer):
        cart = self._get_cart()
        self._clear_expired(cart)
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data.get('cantidad', 1)

        if producto.stock < cantidad:
            raise serializers.ValidationError('No hay suficiente stock disponible')

        item, created = CartItem.objects.get_or_create(
            cart=cart, producto=producto, defaults={'cantidad': 0}
        )

        if created:
            item.cantidad = cantidad
        else:
            item.cantidad += cantidad

        item.save(update_fields=['cantidad'])
        serializer.instance = item  # ensure response uses the updated item

        producto.stock -= cantidad
        producto.save(update_fields=['stock'])
        self._update_reservation(cart)

    def perform_update(self, serializer):
        cart = self._get_cart()
        self._clear_expired(cart)
        instance = serializer.instance
        if instance.cart_id != cart.pk:
            raise serializers.ValidationError('No puedes modificar este producto')
        nueva_cantidad = serializer.validated_data.get('cantidad', instance.cantidad)
        diff = nueva_cantidad - instance.cantidad
        if diff > 0 and instance.producto.stock < diff:
            raise serializers.ValidationError('No hay suficiente stock disponible')
        instance.producto.stock -= diff
        instance.producto.save(update_fields=['stock'])
        serializer.save()
        if cart.items.exists():
            self._update_reservation(cart)
        else:
            CartReservation.objects.filter(cart=cart).delete()

    def perform_destroy(self, instance):
        cart = self._get_cart()
        self._clear_expired(cart)
        if instance.cart_id != cart.pk:
            raise serializers.ValidationError('No puedes eliminar este producto')
        instance.producto.stock += instance.cantidad
        instance.producto.save(update_fields=['stock'])
        super().perform_destroy(instance)
        if cart.items.exists():
            self._update_reservation(cart)
        else:
            CartReservation.objects.filter(cart=cart).delete()

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_all(self, request):
        """Vacía el carrito completo (llamado tras confirmar pago con MP)."""
        cart = self._get_cart()
        clear_cart(cart)
        return Response(status=204)

    def _get_cart(self):
        if not hasattr(self, '_cart'):
            self._cart = ensure_cart_for_request(self.request)
        return self._cart

    def _clear_expired(self, cart):
        now = timezone.now()
        try:
            reserva = cart.reservation
        except CartReservation.DoesNotExist:
            return
        if reserva.expires_at < now:
            for item in cart.items.select_related('producto'):
                prod = item.producto
                prod.stock += item.cantidad
                prod.save(update_fields=['stock'])
            cart.items.all().delete()
            reserva.delete()

    def _update_reservation(self, cart):
        now = timezone.now()
        reserva, _ = CartReservation.objects.get_or_create(
            cart=cart, defaults={'started_at': now, 'expires_at': now}
        )
        reserva.refresh_expiration()
