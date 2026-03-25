# promotions/serializers.py
from decimal import Decimal
from rest_framework import serializers
from .models import Cupon, DailyOffer, PromotionSettings


class DailyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyOffer
        fields = [
            'sale_price',
            'original_price',
            'end_date',
        ]


class PromotionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionSettings
        fields = ['daily_offers_enabled']


class CuponSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Cupon
        fields = [
            'id', 'codigo', 'descripcion', 'tipo', 'tipo_display', 'valor',
            'fecha_inicio', 'fecha_fin', 'activo', 'usos_maximos',
            'usos_actuales', 'monto_minimo',
        ]
        read_only_fields = ['usos_actuales']


class ValidarCuponSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
