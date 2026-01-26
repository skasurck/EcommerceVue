from rest_framework import viewsets, permissions, status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q, Exists, OuterRef, Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from decimal import Decimal, InvalidOperation
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
    ProductoListSerializer,
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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


from django.db.models import Min, Max




class PriceRangeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        result = Producto.objects.aggregate(min_precio=Min('precio_normal'), max_precio=Max('precio_normal'))
        return Response(result)


from celery.result import AsyncResult
from .tasks import classify_products_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class ProductClassificationAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        data = request.data or {}
        product_ids_param = data.get("product_ids") or []
        
        try:
            limit = int(data.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 2000))
        overwrite = bool(data.get("overwrite", False))
        ignore_time_limit = bool(data.get("ignore_time_limit", False))

        logger.info(f"Received classification request with overwrite: {overwrite}, ignore_time_limit: {ignore_time_limit}")

        if product_ids_param:
            product_ids = product_ids_param
        else:
            queryset = Producto.objects.all().order_by("-fecha_creacion")
            logger.info(f"Initial product count: {queryset.count()}")
            
            if not overwrite:
                queryset = queryset.filter(category_ai_main__isnull=True)
                logger.info(f"Product count after 'overwrite' filter: {queryset.count()}")
            
            if not ignore_time_limit:
                ten_days_ago = timezone.now() - timedelta(days=10)
                time_filter = Q(fecha_clasificacion_ai__isnull=True) | Q(fecha_clasificacion_ai__lt=ten_days_ago)
                queryset = queryset.filter(time_filter)
                logger.info(f"Product count after 'time_limit' filter: {queryset.count()}")
            
            product_ids = list(queryset.values_list('id', flat=True)[:limit])

        logger.info(f"Final number of products to be classified: {len(product_ids)}")

        if not product_ids:
            return Response(
                {"message": "No hay productos para clasificar con los criterios seleccionados."},
                status=status.HTTP_200_OK
            )

        task = classify_products_task.delay(product_ids=product_ids, overwrite=overwrite)
        
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

class ProductClassificationStatusView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task_result.status,
            'info': task_result.info,
        }

        # Si el estado no es PENDING pero la info es nula, intenta usar el result
        if task_result.status != 'PENDING' and not task_result.info:
            if isinstance(task_result.result, dict):
                response_data['info'] = task_result.result

        if task_result.successful():
            # Si es exitoso, el resultado final está en 'result'
            final_result = task_result.get()
            if isinstance(final_result, dict):
                response_data['result'] = final_result.get('results')
                # Adicionalmente, asegúrate de que 'info' tenga los datos finales
                response_data['info'] = {
                    'current': final_result.get('current', response_data.get('info', {}).get('current')),
                    'total': final_result.get('total', response_data.get('info', {}).get('total')),
                    'status': final_result.get('status', 'Completado'),
                }

        return Response(response_data)

@method_decorator(cache_page(60), name="dispatch")
class ProductSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response([])
        q = q[:64]
        
        exact_match = request.query_params.get("exact", "false").lower() == "true"

        if exact_match:
            # Búsqueda exacta por nombre (insensible a mayúsculas/minúsculas)
            queryset = Producto.objects.filter(visibilidad=True, estado="publicado", nombre__iexact=q)
            if queryset.exists():
                serializer = ProductSearchSerializer(queryset.first(), context={"request": request})
                return Response([serializer.data])
            else:
                # Si no hay coincidencia exacta, no devolver nada para la solicitud 'exact'
                return Response([])


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


class PendingReviewProductsAPIView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    serializer_class = PendingReviewProductSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Producto.objects.filter(
            category_ai_main__isnull=False,
        ).order_by("-fecha_creacion")


class AllCategoriesAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categorias = Categoria.objects.filter(parent__isnull=True).order_by("nombre")
        serializer = CategoryTreeSerializer(categorias, many=True)
        return Response(serializer.data)


class ApplyCategoryAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        product = get_object_or_404(Producto, pk=pk)
        category_ids = request.data.get("category_ids")
        if category_ids is None:
            category_id = request.data.get("category_id")
            category_ids = [category_id] if category_id is not None else []

        if not isinstance(category_ids, list) or not category_ids:
            return Response(
                {"detail": "Se requiere 'category_ids' como una lista no vacia."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_ids = []
        for category_id in category_ids:
            try:
                normalized_ids.append(int(category_id))
            except (TypeError, ValueError):
                return Response(
                    {"detail": "Uno o mas IDs de categoria no son validos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        normalized_ids = list(dict.fromkeys(normalized_ids))
        valid_categories = Categoria.objects.filter(id__in=normalized_ids).in_bulk(normalized_ids)
        if len(valid_categories) != len(set(normalized_ids)):
            return Response(
                {"detail": "Categoria no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.categorias.set([valid_categories[category_id] for category_id in normalized_ids])
        product.category_ai_main = None
        product.category_ai_sub = None
        product.category_ai_conf_main = None
        product.category_ai_conf_sub = None
        product.save(
            update_fields=[
                "category_ai_main",
                "category_ai_sub",
                "category_ai_conf_main",
                "category_ai_conf_sub",
            ]
        )

        return Response({"detail": "Categoría aplicada correctamente."})


class BulkApplyCategoryAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        product_data = request.data.get("products", [])

        if not isinstance(product_data, list) or not product_data:
            return Response(
                {"detail": "Se requiere una lista de productos en el campo 'products'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_payload = []
        product_ids = []
        all_category_ids = set()
        for item in product_data:
            product_id = item.get("product_id")
            category_ids = item.get("category_ids")
            if category_ids is None:
                category_id = item.get("category_id")
                category_ids = [category_id] if category_id is not None else []

            if not product_id:
                return Response(
                    {"detail": "Cada item debe incluir 'product_id'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not isinstance(category_ids, list) or not category_ids:
                return Response(
                    {"detail": "Cada item debe incluir 'category_ids' como una lista no vacia."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            normalized_ids = []
            for category_id in category_ids:
                try:
                    normalized_ids.append(int(category_id))
                except (TypeError, ValueError):
                    return Response(
                        {"detail": "Uno o mas IDs de categoria no son validos."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            normalized_ids = list(dict.fromkeys(normalized_ids))
            normalized_payload.append(
                {
                    "product_id": product_id,
                    "category_ids": normalized_ids,
                }
            )
            product_ids.append(product_id)
            all_category_ids.update(normalized_ids)

        # Validate that all products and categories exist
        valid_products = Producto.objects.filter(id__in=product_ids).in_bulk(product_ids)
        valid_categories = Categoria.objects.filter(id__in=all_category_ids).in_bulk(list(all_category_ids))

        if len(valid_products) != len(set(product_ids)):
            return Response({"detail": "Uno o mas IDs de producto no son validos."}, status=status.HTTP_404_NOT_FOUND)

        if len(valid_categories) != len(all_category_ids):
            return Response({"detail": "Uno o mas IDs de categoria no son validos."}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                products_to_update = []
                for item in normalized_payload:
                    product = valid_products.get(item["product_id"])
                    if not product:
                        continue
                    categories = [valid_categories[category_id] for category_id in item["category_ids"]]
                    product.categorias.set(categories)
                    product.category_ai_main = None
                    product.category_ai_sub = None
                    product.category_ai_conf_main = None
                    product.category_ai_conf_sub = None
                    products_to_update.append(product)

                Producto.objects.bulk_update(
                    products_to_update,
                    [
                        "category_ai_main",
                        "category_ai_sub",
                        "category_ai_conf_main",
                        "category_ai_conf_sub",
                    ],
                )

        except Exception as e:
            return Response(
                {"detail": f"Ocurrió un error durante la transacción: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"detail": f"{len(normalized_payload)} productos actualizados correctamente."})


from django.db.models import Q

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def get_queryset(self):
        # Optimización: Aplicar .only() y prefetch selectivos según la acción.
        if self.action == 'list':
            # Solo traer los campos necesarios para ProductoListSerializer y precargar
            # las relaciones mínimas que usa el serializador ligero.
            qs = (
                Producto.objects.only(
                    'id', 'nombre', 'precio_normal', 'precio_rebajado',
                    'miniatura', 'imagen_principal', 'descripcion_corta', 'stock'
                ).prefetch_related(
                    Prefetch(
                        "atributos",
                        queryset=ValorAtributo.objects.select_related("atributo").filter(
                            atributo__nombre__iexact="color"
                        ),
                        to_attr="color_atributos",
                    )
                )
            )
        else:
            # Para la vista de detalle, cargar todo como antes.
            qs = (
                Producto.objects
                .select_related("marca")
                .prefetch_related("categorias", "atributos__atributo", "galeria", "precios_escalonados")
            )
        
        qs = qs.order_by("-fecha_creacion")

        # --- Filtros existentes (se aplican a ambos casos) ---
        params = self.request.query_params
        search = params.get('search')
        categoria = params.get('categoria')
        estado = params.get('estado_inventario')
        marca = params.get('marca') or params.get('marcas')

        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(sku__icontains=search))
        if categoria:
            qs = qs.filter(categorias__id=categoria).distinct()
        if estado:
            qs = qs.filter(estado_inventario=estado)
        if marca:
            def parse_id_list(raw):
                if isinstance(raw, (list, tuple)): iterable = raw
                else: iterable = str(raw).split(',')
                ids = []
                for item in iterable:
                    try: ids.append(int(str(item).strip()))
                    except (TypeError, ValueError): continue
                return ids
            marca_ids = parse_id_list(marca)
            if marca_ids:
                qs = qs.filter(marca_id__in=marca_ids)

        precio_min = params.get('precio_min')
        precio_max = params.get('precio_max')

        def parse_decimal_value(value):
            try: return Decimal(str(value))
            except (InvalidOperation, TypeError, ValueError): return None

        min_value = parse_decimal_value(precio_min)
        max_value = parse_decimal_value(precio_max)

        if min_value is not None:
            qs = qs.filter(precio_normal__gte=min_value)
        if max_value is not None:
            qs = qs.filter(precio_normal__lte=max_value)

        en_oferta = params.get('en_oferta')
        if en_oferta and en_oferta.lower() in ['true', '1']:
            qs = qs.filter(precio_rebajado__isnull=False, precio_rebajado__gt=0)

        if self.action == 'list':
            qs = qs.annotate(
                has_tier=Exists(
                    PrecioEscalonado.objects.filter(producto_id=OuterRef("pk"))
                )
            )

        # --- Optimización: Omitir precarga de proveedores para la vista de lista ---
        if self.action != 'list':
            product_ids = list(qs.values_list('id', flat=True))
            if product_ids:
                maps = ProductSupplierMap.objects.filter(product_id__in=product_ids).values('product_id', 'supplier_sku')
                map_by_product = {m['product_id']: m['supplier_sku'] for m in maps}
                skus = list(set(map_by_product.values()))

                if skus:
                    sp_by_sku = {sp.supplier_sku: sp for sp in SupplierProduct.objects.filter(supplier_sku__in=skus)}
                    self._sp_by_product = {
                        pid: sp_by_sku.get(sku)
                        for pid, sku in map_by_product.items()
                        if sp_by_sku.get(sku)
                    }
                else:
                    self._sp_by_product = {}
            else:
                self._sp_by_product = {}
        else:
            # Asegurarse de que el atributo exista para el contexto del serializador, pero vacío.
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
    pagination_class = None

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
