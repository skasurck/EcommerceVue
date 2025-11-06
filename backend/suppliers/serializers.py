from rest_framework import serializers
from django.utils import timezone

from .models import SupplierProduct
from .utils import effective_qty

class SupplierProductSerializer(serializers.ModelSerializer):
    effective_qty = serializers.SerializerMethodField()
    precio_normal = serializers.SerializerMethodField()
    precio_rebajado = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProduct
        fields = [
            'id',
            'supplier',
            'supplier_sku',
            'product_url',
            'name',
            'price_supplier',
            'precio_normal',
            'precio_rebajado',
            'in_stock',
            'available_qty',
            'effective_qty',
            'last_seen',
            'image_urls',
        ]
        read_only_fields = fields

    def get_effective_qty(self, obj):
        return effective_qty(obj.available_qty, obj.in_stock)

    def _get_active_offer(self, obj):
        # Helper to avoid redundant queries
        if not hasattr(self, '_active_offers'):
            self._active_offers = {}
        
        if obj.id not in self._active_offers:
            now = timezone.now()
            self._active_offers[obj.id] = obj.daily_offers.filter(
                is_active=True, start_date__lte=now, end_date__gte=now
            ).first()
        return self._active_offers[obj.id]

    def get_precio_normal(self, obj):
        active_offer = self._get_active_offer(obj)
        if active_offer:
            return active_offer.original_price
        return obj.price_supplier

    def get_precio_rebajado(self, obj):
        active_offer = self._get_active_offer(obj)
        if active_offer:
            return active_offer.sale_price
        return None


class SupermexRunRequestSerializer(serializers.Serializer):
    start_url = serializers.URLField(required=False)
    product_urls = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=False
    )
    limit = serializers.IntegerField(required=False, min_value=0)
    max_pages = serializers.IntegerField(default=5, min_value=1, required=False)
    sleep_s = serializers.FloatField(default=0.6, min_value=0.0, required=False)
    apply_updates = serializers.BooleanField(default=True, required=False)
    http2 = serializers.BooleanField(default=True, required=False)

    def validate(self, attrs):
        start_url = attrs.get('start_url')
        product_urls = attrs.get('product_urls')
        if not start_url and not product_urls:
            raise serializers.ValidationError(
                "Debes proporcionar 'start_url' o 'product_urls'."
            )
        if start_url and product_urls:
            raise serializers.ValidationError(
                "Proporciona solo 'start_url' o 'product_urls', no ambos."
            )
        return attrs
