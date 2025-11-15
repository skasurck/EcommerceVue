from rest_framework import serializers
import json
import re
from django.http import QueryDict
from django.utils.text import slugify
from suppliers.models import SupplierProduct, ProductSupplierMap
from suppliers.utils import effective_qty

from .models import (
    Producto,
    ImagenProducto,
    PrecioEscalonado,
    Categoria,
    Marca,
    Atributo,
    ValorAtributo,
)


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer ligero para sugerencias de búsqueda."""

    name = serializers.CharField(source="nombre")
    slug = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        source="precio_normal", max_digits=10, decimal_places=2
    )
    price_sale = serializers.DecimalField(
        source="precio_rebajado", max_digits=10, decimal_places=2, allow_null=True
    )
    thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ["id", "name", "slug", "price", "price_sale", "thumbnail", "url"]

    def get_slug(self, obj):
        """Devuelve el slug del producto si existe, de lo contrario el ID."""
        return getattr(obj, "slug", obj.pk)

    def get_thumbnail(self, obj):
        request = self.context.get("request")
        url = None
        if obj.miniatura:
            url = obj.miniatura.url
        elif obj.imagen_principal:
            url = obj.imagen_principal.url
        if url and request:
            return request.build_absolute_uri(url)
        return url

    def get_url(self, obj):
        slug = self.get_slug(obj)
        return f"/producto/{slug}/"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"
        extra_kwargs = {"slug": {"required": False}}

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = slugify(validated_data["nombre"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not validated_data.get("slug") and validated_data.get("nombre"):
            validated_data["slug"] = slugify(validated_data["nombre"])
        return super().update(instance, validated_data)


class CategoryTreeSerializer(serializers.ModelSerializer):
    subcategorias = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "subcategorias"]

    def get_subcategorias(self, obj):
        subcategories = obj.subcategorias.all().order_by("nombre")
        serializer = CategoryTreeSerializer(
            subcategories,
            many=True,
            context=self.context,
        )
        return serializer.data


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
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = PrecioEscalonado
        fields = ["id", "cantidad_minima", "precio_unitario"]
        list_serializer_class = PrecioEscalonadoListSerializer


class PendingReviewProductSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "imagen_url",
            "category_ai_main",
            "category_ai_sub",
            "category_ai_conf_main",
            "category_ai_conf_sub",
        ]

    def get_imagen_url(self, obj):
        request = self.context.get("request")
        image_field = obj.miniatura or obj.imagen_principal
        if not image_field:
            return None
        url = image_field.url
        if request:
            return request.build_absolute_uri(url)
        return url


class ProductoSerializer(serializers.ModelSerializer):
    categorias = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), many=True, required=False
    )
    atributos = serializers.PrimaryKeyRelatedField(
        queryset=ValorAtributo.objects.all(), many=True, required=False
    )
    atributos_detalle = ValorAtributoSerializer(
        source="atributos", many=True, read_only=True
    )
    galeria = ImagenProductoSerializer(many=True, read_only=True)
    precios_escalonados = PrecioEscalonadoSerializer(many=True, required=False)
    imagen_principal = serializers.ImageField(required=False, allow_null=True)
    effective_qty = serializers.SerializerMethodField()
    is_virtual_qty = serializers.SerializerMethodField()

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
            "atributos_detalle",
            "stock",
            "category_ai_main",
            "category_ai_sub",
            "category_ai_conf_main",
            "category_ai_conf_sub",
            "fecha_creacion",
            "galeria",
            "precios_escalonados",
            # NUEVOS:
            "effective_qty",
            "is_virtual_qty",
        ]
        read_only_fields = [
            "miniatura",
            "fecha_creacion",
            "category_ai_main",
            "category_ai_sub",
            "category_ai_conf_main",
            "category_ai_conf_sub",
        ]

    def to_internal_value(self, data):
        """Permite recibir precios escalonados desde FormData con notación de corchetes."""
        if isinstance(data, QueryDict):
            data = {
                k: data.getlist(k) if len(data.getlist(k)) > 1 else data.get(k)
                for k in data.keys()
            }

        # Asegurar que las relaciones ManyToMany se procesen como listas incluso
        # cuando solo se envía un elemento desde el formulario (ej. "categorias" y
        # "atributos" en formularios de edición existentes).
        for m2m_field in ("categorias", "atributos"):
            if m2m_field in data and not isinstance(data[m2m_field], list):
                value = data[m2m_field]
                if value in (None, "", "null"):
                    data[m2m_field] = []
                else:
                    data[m2m_field] = [value]

        if "precios_escalonados" in data and isinstance(data["precios_escalonados"], str):
            try:
                data["precios_escalonados"] = json.loads(data["precios_escalonados"])
            except json.JSONDecodeError:
                data["precios_escalonados"] = []

        if "precios_escalonados" not in data:
            pattern = re.compile(r"^precios_escalonados\[(\d+)\]\[(\w+)\]$")
            tiers = {}
            for key in list(data.keys()):
                match = pattern.match(key)
                if match:
                    idx, field = match.groups()
                    tiers.setdefault(int(idx), {})[field] = data.pop(key)
            if tiers:
                data["precios_escalonados"] = [tiers[i] for i in sorted(tiers.keys())]

        # Campos que son de tipo archivo y no deben ser normalizados a None
        file_fields = {"imagen_principal", "galeria"}

        # Normalizar valores "null" o vacíos a None para evitar errores de validación
        for key, value in list(data.items()):
            if key not in file_fields and isinstance(value, str):
                if value.lower() == "null" or value == "":
                    data[key] = None
            elif key not in file_fields and isinstance(value, list):
                # No normalizar listas que puedan contener archivos (como 'galeria')
                # Esta lógica es más para campos de texto/números en listas
                pass

        return super().to_internal_value(data)

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

        # --- NUEVO: Galería desde multipart ---
        request = self.context.get("request")
        if request:
            for f in request.FILES.getlist("galeria"):
                ImagenProducto.objects.create(producto=producto, imagen=f)

        for tier in precios_data:
            tier = dict(tier)
            tier.pop("id", None)
            PrecioEscalonado.objects.create(producto=producto, **tier)

        return producto

    def update(self, instance, validated_data):
        precios_raw = validated_data.pop("precios_escalonados", "[]")
        categorias = validated_data.pop("categorias", None)
        atributos = validated_data.pop("atributos", None)

        # 🔎 DEBUG
        # print("=== DEBUG UPDATE PRODUCTO ===")
        # print("Precios escalonados (raw):", precios_raw)
        # print("Categorías recibidas:", categorias)
        # print("Atributos recibidos:", atributos)
        # print("Otros campos:", validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categorias is not None:
            instance.categorias.set(categorias)
        if atributos is not None:
            instance.atributos.set(atributos)
         # --- NUEVO: anexar nuevas imágenes de galería si vienen ---
        request = self.context.get("request")
        if request:
            for f in request.FILES.getlist("galeria"):
                ImagenProducto.objects.create(producto=instance, imagen=f)

        # Procesar precios escalonados si vienen
        try:
            if isinstance(precios_raw, str):
                precios_data = json.loads(precios_raw)
            else:
                precios_data = precios_raw

            existentes = {p.id: p for p in instance.precios_escalonados.all()}
            enviados = []

            for tier in precios_data:
                tier_id = tier.get("id")
                if tier_id and tier_id in existentes:
                    obj = existentes[tier_id]
                    obj.cantidad_minima = tier["cantidad_minima"]
                    obj.precio_unitario = tier["precio_unitario"]
                    obj.save()
                    enviados.append(tier_id)
                else:
                    nuevo = PrecioEscalonado.objects.create(producto=instance, **tier)
                    enviados.append(nuevo.id)

            # Eliminar los que ya no están
            instance.precios_escalonados.exclude(id__in=enviados).delete()

        except Exception as e:
            print("❌ ERROR procesando precios escalonados:", e)

        return instance

    def _get_supplierproduct(self, obj: Producto):
        """
        Busca el SupplierProduct asociado por medio del mapeo ProductSupplierMap.
        Tomamos el primero si hay varios.
        """
        # 1) Trae todos los SKUs proveedor vinculados a este producto
        skus = list(
            ProductSupplierMap.objects
            .filter(product=obj)
            .values_list("supplier_sku", flat=True)
        )
        if not skus:
            return None
        # 2) Busca el SupplierProduct correspondiente
        return SupplierProduct.objects.filter(supplier_sku__in=skus).first()

    def get_effective_qty(self, obj: Producto) -> int:
        sp = getattr(obj, "_supplier_cache", None) or self._get_supplierproduct(obj)
        if not sp:
            # Sin proveedor → usa tu stock local
            return obj.stock
        return effective_qty(sp.available_qty, sp.in_stock)

    def get_is_virtual_qty(self, obj: Producto) -> bool:
        sp = getattr(obj, "_supplier_cache", None) or self._get_supplierproduct(obj)
        if not sp:
            # Sin proveedor → no es virtual (estás usando tu propio stock)
            return False
        return not (sp.available_qty and sp.available_qty > 0)
