from rest_framework import serializers

from .models import (
    Producto,
    ImagenProducto,
    PrecioEscalonado,
    Categoria,
    Marca,
    ValorAtributo,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = "__all__"


class ValorAtributoSerializer(serializers.ModelSerializer):
    atributo = serializers.StringRelatedField()

    class Meta:
        model = ValorAtributo
        fields = ["id", "atributo", "valor"]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ["id", "imagen"]


class PrecioEscalonadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioEscalonado
        fields = ["id", "cantidad_minima", "precio_unitario"]


class ProductoSerializer(serializers.ModelSerializer):
    categorias = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), many=True, required=False
    )
    atributos = serializers.PrimaryKeyRelatedField(
        queryset=ValorAtributo.objects.all(), many=True, required=False
    )
    galeria = ImagenProductoSerializer(many=True, read_only=True)
    precios_escalonados = PrecioEscalonadoSerializer(many=True, required=False)
    imagen_principal = serializers.ImageField(required=False)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion_corta",
            "descripcion_larga",
            "precio_normal",
            "precio_rebajado",
            "sku",
            "imagen_principal",
            "miniatura",
            "disponible",
            "estado_inventario",
            "visibilidad",
            "estado",
            "categoria",
            "categorias",
            "marca",
            "atributos",
            "stock",
            "fecha_creacion",
            "galeria",
            "precios_escalonados",
        ]
        read_only_fields = ["miniatura", "fecha_creacion"]

    def create(self, validated_data):
        precios_data = validated_data.pop("precios_escalonados", [])
        categorias = validated_data.pop("categorias", [])
        atributos = validated_data.pop("atributos", [])

        producto = Producto.objects.create(**validated_data)
        producto.categorias.set(categorias)
        producto.atributos.set(atributos)

        for tier in precios_data:
            PrecioEscalonado.objects.create(producto=producto, **tier)

        return producto

    def update(self, instance, validated_data):
        precios_data = validated_data.pop("precios_escalonados", None)
        categorias = validated_data.pop("categorias", None)
        atributos = validated_data.pop("atributos", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categorias is not None:
            instance.categorias.set(categorias)
        if atributos is not None:
            instance.atributos.set(atributos)
        if precios_data is not None:
            instance.precios_escalonados.all().delete()
            for tier in precios_data:
                PrecioEscalonado.objects.create(producto=instance, **tier)

        return instance

