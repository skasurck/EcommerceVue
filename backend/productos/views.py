from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .ai import build_text_from_product, classify_text
from .models import (
    Producto,
    Categoria,
    Marca,
    Atributo,
    ValorAtributo,
    ImagenProducto,
    PrecioEscalonado,
)
from .serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    CategoryTreeSerializer,
    MarcaSerializer,
    AtributoSerializer,
    ValorAtributoSerializer,
    ImagenProductoSerializer,
    PrecioEscalonadoSerializer,
    ProductSearchSerializer,
    PendingReviewProductSerializer,
)
from .forms import ProductoForm, PrecioEscalonadoFormSet
from usuarios.permissions import IsAdminOrSuperAdmin
from suppliers.models import ProductSupplierMap, SupplierProduct
from rest_framework.viewsets import ReadOnlyModelViewSet


from django.db.models import Min, Max

class PriceRangeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        result = Producto.objects.aggregate(min_precio=Min('precio_normal'), max_precio=Max('precio_normal'))
        return Response(result)


class ProductClassificationAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        data = request.data or {}
        product_ids = data.get("product_ids") or []
        try:
            limit = int(data.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 500))
        overwrite = bool(data.get("overwrite", False))

        queryset = Producto.objects.all().order_by("-fecha_creacion")
        if product_ids:
            queryset = queryset.filter(id__in=product_ids)
        else:
            queryset = queryset[:limit]

        products = list(queryset)
        results = []

        for product in products:
            if product.category_ai_main and not overwrite:
                results.append(
                    {
                        "product_id": product.id,
                        "main": product.category_ai_main,
                        "sub": product.category_ai_sub,
                        "conf_main": product.category_ai_conf_main,
                        "conf_sub": product.category_ai_conf_sub,
                    }
                )
                continue

            text = build_text_from_product(product)
            if not text:
                text = product.nombre or f"Producto {product.pk}"

            classification = classify_text(text)

            with transaction.atomic():
                product.category_ai_main = classification.main
                product.category_ai_sub = classification.sub
                product.category_ai_conf_main = classification.main_score
                product.category_ai_conf_sub = classification.sub_score
                product.save(
                    update_fields=[
                        "category_ai_main",
                        "category_ai_sub",
                        "category_ai_conf_main",
                        "category_ai_conf_sub",
                    ]
                )

            results.append(
                {
                    "product_id": product.id,
                    "main": product.category_ai_main,
                    "sub": product.category_ai_sub,
                    "conf_main": product.category_ai_conf_main,
                    "conf_sub": product.category_ai_conf_sub,
                }
            )

        return Response({"results": results, "count": len(results)})

@method_decorator(cache_page(60), name="dispatch")
class ProductSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response([])
        q = q[:64]
        try:
            limit = int(request.query_params.get("limit", 5))
        except ValueError:
            limit = 5
        limit = max(1, min(limit, 5))
        queryset = (
            Producto.objects.filter(visibilidad=True, estado="publicado")
            .filter(
                Q(nombre__icontains=q)
                | Q(sku__icontains=q)
                | Q(descripcion_larga__icontains=q)
            )
            .order_by("-fecha_creacion")[:limit]
        )
        serializer = ProductSearchSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class PendingReviewProductsAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        queryset = Producto.objects.filter(
            category_ai_main__isnull=False,
            categoria__isnull=True,
        ).order_by("-fecha_creacion")
        serializer = PendingReviewProductSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class AllCategoriesAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        categorias = Categoria.objects.filter(parent__isnull=True).order_by("nombre")
        serializer = CategoryTreeSerializer(categorias, many=True)
        return Response(serializer.data)


class ApplyCategoryAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        product = get_object_or_404(Producto, pk=pk)
        category_id = request.data.get("category_id")

        if not category_id:
            return Response(
                {"detail": "Se requiere 'category_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Categoria.objects.get(pk=category_id)
        except Categoria.DoesNotExist:
            return Response(
                {"detail": "Categoría no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.categoria = category
        product.category_ai_main = None
        product.category_ai_sub = None
        product.category_ai_conf_main = None
        product.category_ai_conf_sub = None
        product.save(
            update_fields=[
                "categoria",
                "category_ai_main",
                "category_ai_sub",
                "category_ai_conf_main",
                "category_ai_conf_sub",
            ]
        )

        return Response({"detail": "Categoría aplicada correctamente."})

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


from django.db.models import Q

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Base optimizada (NO uses .all() si no quieres)
        qs = (
            Producto.objects
            .select_related("marca", "categoria")
            .prefetch_related("categorias", "atributos__atributo", "galeria", "precios_escalonados")
            .order_by("-fecha_creacion")
        )

        # Filtros existentes
        params = self.request.query_params
        search   = params.get('search')
        categoria = params.get('categoria')
        estado   = params.get('estado_inventario')
        marca    = params.get('marca')

        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(sku__icontains=search))
        if categoria:
            # al filtrar por M2M puede duplicar filas; usa distinct() SOLO en este caso
            qs = qs.filter(categorias__id=categoria).distinct()
        if estado:
            qs = qs.filter(estado_inventario=estado)
        if marca:
            qs = qs.filter(marca_id=marca)

        # Filtro para ofertas
        en_oferta = params.get('en_oferta')
        if en_oferta and en_oferta.lower() in ['true', '1']:
            qs = qs.filter(precio_rebajado__isnull=False, precio_rebajado__gt=0)

        # --- Precarga de suppliers SIN romper nada de arriba ---
        product_ids = list(qs.values_list('id', flat=True))
        if product_ids:
            maps = ProductSupplierMap.objects.filter(
                product_id__in=product_ids
            ).values('product_id', 'supplier_sku')

            map_by_product = {m['product_id']: m['supplier_sku'] for m in maps}
            skus = list(set(map_by_product.values()))

            if skus:
                sp_by_sku = {
                    sp.supplier_sku: sp
                    for sp in SupplierProduct.objects.filter(supplier_sku__in=skus)
                }
                # cache final: product_id -> SupplierProduct
                self._sp_by_product = {
                    pid: sp_by_sku.get(sku)
                    for pid, sku in map_by_product.items()
                    if sp_by_sku.get(sku)
                }
            else:
                self._sp_by_product = {}
        else:
            self._sp_by_product = {}

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # pasa el cache al serializer
        ctx['sp_by_product'] = getattr(self, '_sp_by_product', {})
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        print("❌ Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        print("❌ Errores del serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('id') 
    serializer_class = CategoriaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'nombre', 'created_at']
    ordering = ['id']

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all().order_by("nombre", "id")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["nombre", "id", "created_at"]  # lo que tengas
    ordering = ["nombre", "id"]  # default estable
    serializer_class = MarcaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class AtributoViewSet(viewsets.ModelViewSet):
    queryset = Atributo.objects.all().order_by("nombre", "id")
    serializer_class = AtributoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class ValorAtributoViewSet(viewsets.ModelViewSet):
    queryset = ValorAtributo.objects.all().order_by("valor", "id")
    serializer_class = ValorAtributoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class ImagenProductoViewSet(viewsets.ModelViewSet):
    queryset = ImagenProducto.objects.all()
    serializer_class = ImagenProductoSerializer

    def get_queryset(self):
        producto_id = self.kwargs.get("producto_pk")
        if producto_id:
            return self.queryset.filter(producto_id=producto_id)
        return self.queryset

    def perform_create(self, serializer):
        producto_id = self.kwargs.get("producto_pk")
        producto = get_object_or_404(Producto, pk=producto_id)
        serializer.save(producto=producto)

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class PrecioEscalonadoViewSet(viewsets.ModelViewSet):
    queryset = PrecioEscalonado.objects.all()
    serializer_class = PrecioEscalonadoSerializer

    def get_queryset(self):
        producto_id = self.kwargs.get("producto_pk") or self.request.query_params.get("producto")
        if producto_id:
            return self.queryset.filter(producto_id=producto_id)
        return self.queryset

    def perform_create(self, serializer):
        producto_id = self.kwargs.get("producto_pk") or self.request.data.get("producto")
        producto = get_object_or_404(Producto, pk=producto_id)
        serializer.save(producto=producto)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


def _es_admin(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol in ['admin', 'super_admin']


@login_required
@user_passes_test(_es_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        formset = PrecioEscalonadoFormSet(request.POST, instance=producto, prefix='precios_escalonados')
        if form.is_valid() and formset.is_valid():
            producto = form.save()
            formset.save()
            atributos_ids = request.POST.getlist('atributos')
            producto.atributos.set(atributos_ids)
            if form.cleaned_data.get('eliminar_imagen'):
                producto.imagen_principal.delete(save=True)
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('/admin/productos?actualizado=1')
    else:
        form = ProductoForm(instance=producto)
        formset = PrecioEscalonadoFormSet(instance=producto, prefix='precios_escalonados')
    valores_atributo = ValorAtributo.objects.all()
    return render(
        request,
        'productos/editar_producto.html',
        {
            'form': form,
            'formset': formset,
            'producto': producto,
            'valores_atributo': valores_atributo,
        },
    )
