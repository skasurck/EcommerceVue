from rest_framework import serializers
import json

from .models import (
    Producto,
    ImagenProducto,
    PrecioEscalonado,
    Categoria,
    Marca,
    Atributo,
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


class AtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atributo
        fields = "__all__"


class ValorAtributoSerializer(serializers.ModelSerializer):
    atributo = AtributoSerializer(read_only=True)
    atributo_id = serializers.PrimaryKeyRelatedField(
        queryset=Atributo.objects.all(), source="atributo", write_only=True
    )

    class Meta:
        model = ValorAtributo
        fields = ["id", "atributo", "atributo_id", "valor"]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ["id", "imagen"]


class PrecioEscalonadoListSerializer(serializers.ListSerializer):
    """Permite recibir una lista JSON cuando se envía vía FormData."""

    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = []
        elif isinstance(data, list) and data and isinstance(data[0], str):
            parsed = []
            for item in data:
                try:
                    parsed.append(json.loads(item))
                except json.JSONDecodeError:
                    continue
            data = parsed
        return super().to_internal_value(data)


class PrecioEscalonadoSerializer(serializers.ModelSerializer):
    # permitir ID para distinguir entre actualizaciones y creaciones
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PrecioEscalonado
        fields = ["id", "cantidad_minima", "precio_unitario"]
        list_serializer_class = PrecioEscalonadoListSerializer


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

    def validate_precios_escalonados(self, value):
        cantidades = [tier["cantidad_minima"] for tier in value]
        if len(cantidades) != len(set(cantidades)):
            raise serializers.ValidationError("No se puede repetir cantidad_minima")
        return value

    def create(self, validated_data):
        precios_data = validated_data.pop("precios_escalonados", [])
        categorias = validated_data.pop("categorias", [])
        atributos = validated_data.pop("atributos", [])

        producto = Producto.objects.create(**validated_data)
        producto.categorias.set(categorias)
        producto.atributos.set(atributos)

        for tier in precios_data:
            tier = dict(tier)
            tier.pop("id", None)
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
            existentes = {p.id: p for p in instance.precios_escalonados.all()}
            enviados = []
            for tier in precios_data:
                tier = dict(tier)
                tier_id = tier.pop("id", None)
                if tier_id and tier_id in existentes:
                    obj = existentes[tier_id]
                    obj.cantidad_minima = tier["cantidad_minima"]
                    obj.precio_unitario = tier["precio_unitario"]
                    obj.save()
                    enviados.append(tier_id)
                else:
                    nuevo = PrecioEscalonado.objects.create(producto=instance, **tier)
                    enviados.append(nuevo.id)
            instance.precios_escalonados.exclude(id__in=enviados).delete()

        return instance

