from rest_framework import viewsets, permissions, serializers
from django.utils import timezone
from .models import CartItem, CartReservation
from .serializers import CartItemSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self._clear_expired()
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Add items to the cart merging with existing ones.

        The original implementation always attempted to create a new
        ``CartItem`` which triggered an ``IntegrityError`` when the same
        user tried to add the same product twice (the model has a
        ``unique_together`` constraint on ``user`` and ``producto``).  This
        method now checks if an item for the given product already exists and
        simply increases its quantity instead of creating a duplicate.
        """

        self._clear_expired()
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data.get('cantidad', 1)

        if producto.stock < cantidad:
            raise serializers.ValidationError('No hay suficiente stock disponible')

        item, created = CartItem.objects.get_or_create(
            user=self.request.user, producto=producto, defaults={'cantidad': 0}
        )

        if created:
            item.cantidad = cantidad
        else:
            item.cantidad += cantidad

        item.save()
        serializer.instance = item  # ensure response uses the updated item

        producto.stock -= cantidad
        producto.save()
        self._update_reservation()

    def perform_update(self, serializer):
        self._clear_expired()
        instance = serializer.instance
        nueva_cantidad = serializer.validated_data.get('cantidad', instance.cantidad)
        diff = nueva_cantidad - instance.cantidad
        if diff > 0 and instance.producto.stock < diff:
            raise serializers.ValidationError('No hay suficiente stock disponible')
        instance.producto.stock -= diff
        instance.producto.save()
        serializer.save()
        self._update_reservation()

    def perform_destroy(self, instance):
        self._clear_expired()
        instance.producto.stock += instance.cantidad
        instance.producto.save()
        instance.delete()

    def _clear_expired(self):
        now = timezone.now()
        reserva = CartReservation.objects.filter(user=self.request.user).first()
        if reserva and reserva.expires_at < now:
            items = CartItem.objects.filter(user=self.request.user)
            for item in items:
                prod = item.producto
                prod.stock += item.cantidad
                prod.save()
            items.delete()
            reserva.delete()

    def _update_reservation(self):
        now = timezone.now()
        reserva, created = CartReservation.objects.get_or_create(user=self.request.user, defaults={'expires_at': now})
        reserva.refresh_expiration()
