from rest_framework import serializers
from .models import CartItem
from productos.serializers import ProductoSerializer

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'producto', 'cantidad']
        read_only_fields = ['user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['producto'] = ProductoSerializer(instance.producto, context=self.context).data
        return data