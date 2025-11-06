# promotions/serializers.py
from rest_framework import serializers
from .models import DailyOffer, PromotionSettings

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
