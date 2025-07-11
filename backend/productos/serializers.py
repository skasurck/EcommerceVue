from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False)

    class Meta:
        model = Producto
        fields = '__all__' 

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value
    
    # Validación de imagen
    def validate_imagen(self, image):
        if not image:
            return image          # opcional, puede venir vacío

        # 1. Extensión / formato
        formatos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
        if image.content_type not in formatos_permitidos:
            raise serializers.ValidationError("Solo se permiten JPG, PNG o WEBP.")

        # 2. Tamaño (máx 10 MB)
        max_size = 10 * 1024 * 1024   # 10 MB
        if image.size > max_size:
            raise serializers.ValidationError("La imagen supera los 10 MB.")

        return image

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'imagen', 'disponible']