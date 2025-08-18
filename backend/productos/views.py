from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
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
    MarcaSerializer,
    AtributoSerializer,
    ValorAtributoSerializer,
    ImagenProductoSerializer,
    PrecioEscalonadoSerializer,
    ProductSearchSerializer,
)
from .forms import ProductoForm, PrecioEscalonadoFormSet
from usuarios.permissions import IsAdminOrSuperAdmin


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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('-fecha_creacion')
    serializer_class = ProductoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        categoria = self.request.query_params.get('categoria')
        estado = self.request.query_params.get('estado_inventario')
        marca = self.request.query_params.get('marca')

        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(sku__icontains=search))
        if categoria:
            queryset = queryset.filter(categorias__id=categoria)
        if estado:
            queryset = queryset.filter(estado_inventario=estado)
        if marca:
            queryset = queryset.filter(marca_id=marca)
        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            print("❌ Errores del serializer:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class AtributoViewSet(viewsets.ModelViewSet):
    queryset = Atributo.objects.all()
    serializer_class = AtributoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.AllowAny()]


class ValorAtributoViewSet(viewsets.ModelViewSet):
    queryset = ValorAtributo.objects.all()
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
