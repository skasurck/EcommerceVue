from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Producto, ImagenProducto, PrecioEscalonado, Categoria, Marca, ValorAtributo

# ──────────── CATEGORÍA ────────────
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

# ──────────── MARCA ────────────
class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

# ──────────── ATRIBUTOS ────────────
class ValorAtributoSerializer(serializers.ModelSerializer):
    atributo = serializers.StringRelatedField()

    class Meta:
        model = ValorAtributo
        fields = ['id', 'atributo', 'valor']

# ──────────── GALERÍA ────────────
class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen']

# ──────────── PRECIOS ESCALONADOS ────────────
class PrecioEscalonadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioEscalonado
        fields = ['id', 'cantidad_minima', 'precio_unitario']

# ──────────── PRODUCTO ────────────
class ProductoSerializer(serializers.ModelSerializer):
    imagen_principal = serializers.ImageField(required=False)
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), required=False)
    marca = serializers.PrimaryKeyRelatedField(queryset=Marca.objects.all(), required=False)
    atributos = serializers.PrimaryKeyRelatedField(queryset=ValorAtributo.objects.all(), many=True, required=False)
    # Añadir galería de imágenes
    galeria = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    ) 
    galeria_read = ImagenProductoSerializer(many=True, read_only=True, source='galeria')
    stock = serializers.IntegerField(default=0, required=False)
    precios_escalonados = PrecioEscalonadoSerializer(many=True, read_only=True)
    miniatura_url = serializers.SerializerMethodField()
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion_corta', 'descripcion_larga',
            'precio_normal', 'precio_rebajado', 'sku', 'imagen_principal',
            'miniatura_url','estado_inventario', 'disponible',
            'visibilidad', 'estado', 'categoria', 'marca', 'atributos',
            'galeria','galeria_read','stock', 'precios_escalonados'
        ]
    # Método para obtener la URL de la miniatura
    def get_miniatura_url(self, obj):
        request = self.context.get('request')
        if obj.miniatura and hasattr(obj.miniatura, 'url'):
            url = obj.miniatura.url
            return request.build_absolute_uri(url) if request else url
        return None
    # Validación del precio
    def validate_precio_normal(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    # Validación de la imagen
    def validate_imagen_principal(self, image):
        if not image:
            return image  # Imagen es opcional

        formatos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in formatos_permitidos:
            raise serializers.ValidationError("Solo se permiten JPG, PNG o WEBP.")

        if image.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La imagen supera los 10 MB.")
        
        return image
    # Crear el producto y las imágenes de galería
    def create(self, validated_data): 
        request = self.context['request']
        
        galeria_imagenes = request.FILES.getlist('galeria')
        imagen_principal = request.FILES.get('imagen_principal')  # 👈 Extrae imagen principal
        miniatura = request.FILES.get('miniatura')  # 👈 Si también mandas miniatura por separado

        precios_data = validated_data.pop('precios_escalonados', [])
        atributos_data = validated_data.pop('atributos', [])

        imagen_principal = validated_data.pop('imagen_principal', None)
        miniatura = validated_data.pop('miniatura', None)

        # Crea el producto sin imagen_principal ni miniatura aún
        producto = Producto.objects.create(
        imagen_principal=imagen_principal,
        miniatura=miniatura,
            **validated_data
        )

        # Asignar imagen principal y miniatura si existen
        if imagen_principal:
            producto.imagen_principal = imagen_principal

        if miniatura:
            producto.miniatura = miniatura

        producto.save()  # 👈 Muy importante

        # Relación ManyToMany
        producto.atributos.set(atributos_data)

        # Galería de imágenes
        for imagen in galeria_imagenes:
            ImagenProducto.objects.create(producto=producto, imagen=imagen)

        # Precios escalonados
        for precio in precios_data:
            PrecioEscalonado.objects.create(producto=producto, **precio)

        return producto

    
    def update(self, instance, validated_data):
        precios_data = validated_data.pop('precios_escalonados', [])
        galeria_imagenes = self.context['request'].FILES.getlist('galeria')

        # Actualiza campos del producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Elimina los precios actuales y los vuelve a crear
        instance.precios_escalonados.all().delete()
        for precio in precios_data:
            PrecioEscalonado.objects.create(producto=instance, **precio)

        # Opcional: eliminar galería y agregar nuevas si las mandas
        for imagen in galeria_imagenes:
            ImagenProducto.objects.create(producto=instance, imagen=imagen)

        return instance
    
    def validate_precios_escalonados(self, value):
        cantidades = set()
        for item in value:
            cantidad = item.get('cantidad_minima')
            precio = item.get('precio_unitario')

            if cantidad in cantidades:
                raise serializers.ValidationError(f"Ya se definió un precio para {cantidad} unidades.")
            if cantidad <= 0:
                raise serializers.ValidationError("La cantidad mínima debe ser mayor a 0.")
            if precio <= 0:
                raise serializers.ValidationError("El precio unitario debe ser mayor a 0.")
            
            cantidades.add(cantidad)
        return value
    
    def validate(self, attrs):
        stock = attrs.get('stock', None)
        estado = attrs.get('estado_inventario', None)

        if stock == 0 and estado != 'agotado':
            raise serializers.ValidationError({
                'estado_inventario': 'Si el stock es 0, el estado de inventario debe ser "agotado".'
            })

        if stock > 0 and estado != 'en_existencia':
            raise serializers.ValidationError({
                'estado_inventario': 'Si hay stock disponible, el estado debe ser "en existencia".'
            })

        return attrs

    
class ImagenProductoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'producto', 'imagen']
    
    def validate_imagen(self, image):
        if not image:
            raise serializers.ValidationError("La imagen es obligatoria.")

        formatos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in formatos_permitidos:
            raise serializers.ValidationError("Formato inválido. Usa JPG, PNG o WEBP.")

        if image.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La imagen supera los 10 MB.")
        
        return image