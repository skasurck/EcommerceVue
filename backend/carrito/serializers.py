from rest_framework import serializers
from .models import CartItem, CartReservation
from productos.serializers import ProductoListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    reserva_expira = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'producto', 'cantidad', 'reserva_expira']
        read_only_fields = ['reserva_expira']

    def get_reserva_expira(self, obj):
        try:
            reserva = obj.cart.reservation
        except CartReservation.DoesNotExist:
            return None
        return reserva.expires_at

    def to_representation(self, instance):
        """
        Usa un serializador de producto ligero para la representación.
        """
        data = super().to_representation(instance)
        data['producto'] = ProductoListSerializer(instance.producto, context=self.context).data
        return data

