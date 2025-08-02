from rest_framework import serializers
from .models import Direccion, MetodoEnvio, Pedido


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        exclude = ('user',)


class MetodoEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoEnvio
        fields = ['id', 'nombre', 'costo']


class PedidoSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()

    class Meta:
        model = Pedido
        fields = ['id', 'direccion', 'metodo_envio', 'metodo_pago', 'indicaciones', 'creado']
        read_only_fields = ['id', 'creado']

    def create(self, validated_data):
        request = self.context.get('request')
        direccion_data = validated_data.pop('direccion')
        user = request.user if request and request.user.is_authenticated else None
        save_address = request.data.get('save_address')
        direccion = Direccion.objects.create(user=user if save_address else None, **direccion_data)
        pedido = Pedido.objects.create(user=user, direccion=direccion, **validated_data)
        return pedido
