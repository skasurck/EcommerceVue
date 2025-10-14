from rest_framework import serializers
from .models import CartItem, CartReservation
from productos.serializers import ProductoSerializer

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
        data = super().to_representation(instance)
        data['producto'] = ProductoSerializer(instance.producto, context=self.context).data
        return data

