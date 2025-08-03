from rest_framework import serializers
from .models import CartItem
from productos.serializers import ProductoSerializer

class CartItemSerializer(serializers.ModelSerializer):
    reserva_expira = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'producto', 'cantidad', 'reserva_expira']
        read_only_fields = ['user']

    def get_reserva_expira(self, obj):
        reserva = getattr(obj.user, 'cart_reservation', None)
        return reserva.expires_at if reserva else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['producto'] = ProductoSerializer(instance.producto, context=self.context).data
        return data

