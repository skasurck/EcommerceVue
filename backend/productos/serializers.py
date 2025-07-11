from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False)

    class Meta:
        model = Producto
        fields = '__all__' 
