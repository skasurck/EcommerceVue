from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Sum, Avg, Count, Q, F
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from django.utils import timezone
import datetime
from .models import Direccion, MetodoEnvio, Pedido, PedidoHistorial, PedidoItem
from .serializers import DireccionSerializer, MetodoEnvioSerializer, PedidoSerializer, PedidoItemSerializer
from usuarios.permissions import IsAdminOrSuperAdmin
from tienda.throttles import PedidoCreateRateThrottle


class PedidoByPreferenceView(APIView):
    """Devuelve el resumen del pedido solo a su dueño autenticado o a un admin."""
    permission_classes = [permissions.IsAuthenticated]

    def _user_can_access_order(self, user, pedido):
        perfil = getattr(user, "perfil", None)
        if perfil and perfil.rol in ("admin", "super_admin"):
            return True
        if user.is_staff or user.is_superuser:
            return True
        return pedido.user_id == user.id

    def _serialize_public_order(self, request, pedido):
        detalles = PedidoItemSerializer(
            pedido.items.select_related('producto').all(),
            many=True,
            context={'request': request},
        ).data
        return {
            'id': pedido.id,
            'estado': pedido.estado,
            'subtotal': str(pedido.subtotal),
            'descuento': str(pedido.descuento),
            'costo_envio': str(pedido.costo_envio),
            'total': str(pedido.total),
            'metodo_pago': pedido.metodo_pago,
            'metodo_pago_display': pedido.get_metodo_pago_display(),
            'cupon': pedido.cupon.codigo if pedido.cupon else None,
            'detalles': detalles,
        }

    def get(self, request, preference_id, *args, **kwargs):
        try:
            pedido = Pedido.objects.select_related('cupon').prefetch_related('items__producto').get(
                mercadopago_preference_id=preference_id
            )
            if not self._user_can_access_order(request.user, pedido):
                return Response({"detail": "No tienes permiso para ver este pedido"}, status=status.HTTP_403_FORBIDDEN)
            return Response(self._serialize_public_order(request, pedido))
        except Pedido.DoesNotExist:
            return Response({"detail": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)


class PedidoPublicView(APIView):
    """Devuelve el resumen del pedido solo a su dueño autenticado o a un admin."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pedido_id, *args, **kwargs):
        try:
            pedido = Pedido.objects.select_related('cupon').prefetch_related('items__producto').get(pk=pedido_id)
        except Pedido.DoesNotExist:
            return Response({"detail": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if not PedidoByPreferenceView()._user_can_access_order(request.user, pedido):
            return Response({"detail": "No tienes permiso para ver este pedido"}, status=status.HTTP_403_FORBIDDEN)

        payload = PedidoByPreferenceView()._serialize_public_order(request, pedido)
        return Response(payload)


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Direccion.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "tiene_direccion": queryset.exists(),
            "direcciones": serializer.data,
        })

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = instance.user
        was_default = instance.predeterminada
        super().perform_destroy(instance)
        if was_default:
            restante = Direccion.objects.filter(user=user).first()
            if restante:
                Direccion.objects.filter(user=user).update(predeterminada=False)
                restante.predeterminada = True
                restante.save(update_fields=["predeterminada"])


class MetodoEnvioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetodoEnvio.objects.all().order_by('id')
    serializer_class = MetodoEnvioSerializer
    permission_classes = [permissions.AllowAny]


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        '=id',
        'direccion__nombre', 'direccion__apellidos', 'direccion__email',
        'direccion__calle', 'direccion__colonia', 'direccion__ciudad',
        'direccion__codigo_postal', 'direccion__telefono',
    ]
    ordering_fields = ['creado', 'total', 'id']
    ordering = ['-creado']

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def get_throttles(self):
        if self.action == "create":
            return [PedidoCreateRateThrottle()]
        return super().get_throttles()

    def _user_can_view_all(self, user):
        perfil = getattr(user, "perfil", None)
        if perfil and perfil.rol in ("admin", "super_admin"):
            return True
        return user.is_staff or user.is_superuser

    def _user_can_access_order(self, user, pedido):
        if self._user_can_view_all(user):
            return True
        return pedido.user_id == user.id

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Pedido.objects.none()

        qs = Pedido.objects.all() if self._user_can_view_all(user) else Pedido.objects.filter(user=user)
        params = self.request.query_params

        estado = params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)

        metodo_pago = params.get("metodo_pago")
        if metodo_pago:
            qs = qs.filter(metodo_pago=metodo_pago)

        papelera = params.get("papelera")
        incluye_papelera = params.get("incluye_papelera")
        if papelera:
            qs = qs.filter(papelera=True)
        elif not incluye_papelera:
            qs = qs.filter(papelera=False)

        fecha_desde = params.get("fecha_desde")
        if fecha_desde:
            qs = qs.filter(creado__date__gte=parse_date(fecha_desde))
        fecha_hasta = params.get("fecha_hasta")
        if fecha_hasta:
            qs = qs.filter(creado__date__lte=parse_date(fecha_hasta))

        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='cancelar-mp')
    def cancelar_mp(self, request, pk=None):
        """Compatibilidad: marca como fallido un pedido de MP con pago rechazado."""
        try:
            pedido = Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            return Response({'detail': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not self._user_can_access_order(request.user, pedido):
            return Response({'detail': 'No tienes permiso para modificar este pedido'}, status=status.HTTP_403_FORBIDDEN)
        if pedido.estado not in ('iniciado', 'pendiente') or pedido.metodo_pago != 'mercadopago':
            return Response({'detail': 'El pedido no puede cancelarse'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.estado = 'fallido'
        pedido.save(update_fields=['estado'])
        return Response({'status': 'fallido', 'id': pedido.id})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='retorno-mp')
    def retorno_mp(self, request, pk=None):
        try:
            pedido = Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            return Response({'detail': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not self._user_can_access_order(request.user, pedido):
            return Response({'detail': 'No tienes permiso para modificar este pedido'}, status=status.HTTP_403_FORBIDDEN)

        if pedido.metodo_pago != 'mercadopago':
            return Response({'detail': 'El pedido no es de Mercado Pago'}, status=status.HTTP_400_BAD_REQUEST)

        retorno = str(request.data.get('status', '')).lower()
        if retorno not in ('approved', 'pending', 'failure'):
            return Response({'detail': 'Estado de retorno inválido'}, status=status.HTTP_400_BAD_REQUEST)

        if retorno == 'failure' and pedido.estado in ('iniciado', 'pendiente'):
            pedido.estado = 'fallido'
            pedido.save(update_fields=['estado'])
        elif retorno in ('pending', 'approved') and pedido.estado == 'iniciado':
            pedido.estado = 'pendiente'
            pedido.save(update_fields=['estado'])

        return Response({'id': pedido.id, 'estado': pedido.estado})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError:
            raise
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_update_estado(self, request):
        ids = request.data.get('ids', [])
        estado = request.data.get('estado')
        numero_guia = request.data.get('numero_guia', '')
        allowed = ['iniciado', 'pendiente', 'pagado', 'confirmado', 'enviado', 'fallido', 'cancelado']
        if estado not in allowed:
            return Response({'detail': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.estado = estado
                update_fields = ['estado']
                if estado == 'enviado' and numero_guia:
                    pedido.numero_guia = numero_guia
                    update_fields.append('numero_guia')
                pedido.save(update_fields=update_fields)
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def trash(self, request, pk=None):
        pedido = self.get_object()
        if pedido.papelera:
            return Response({'detail': 'Ya está en papelera'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.papelera = True
        pedido.eliminado_en = timezone.now()
        pedido.save(update_fields=['papelera', 'eliminado_en'])
        PedidoHistorial.objects.create(pedido=pedido, descripcion='Movido a papelera')
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def restore(self, request, pk=None):
        pedido = self.get_object()
        if not pedido.papelera:
            return Response({'detail': 'Pedido no está en papelera'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.papelera = False
        pedido.eliminado_en = None
        pedido.save(update_fields=['papelera', 'eliminado_en'])
        PedidoHistorial.objects.create(pedido=pedido, descripcion='Restaurado desde papelera')
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_trash(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.papelera = True
                pedido.eliminado_en = timezone.now()
                pedido.save(update_fields=['papelera', 'eliminado_en'])
                PedidoHistorial.objects.create(pedido=pedido, descripcion='Movido a papelera')
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_restore(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                pedido.papelera = False
                pedido.eliminado_en = None
                pedido.save(update_fields=['papelera', 'eliminado_en'])
                PedidoHistorial.objects.create(pedido=pedido, descripcion='Restaurado desde papelera')
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin])
    def bulk_destroy(self, request):
        ids = request.data.get('ids', [])
        updated = 0
        failed = []
        for pk in ids:
            try:
                pedido = Pedido.objects.get(pk=pk)
                if not pedido.papelera:
                    raise Exception('No está en papelera')
                pedido.delete()
                updated += 1
            except Pedido.DoesNotExist:
                failed.append({'id': pk, 'error': 'No existe'})
            except Exception as exc:
                failed.append({'id': pk, 'error': str(exc)})
        return Response({'updated': updated, 'failed': failed})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.papelera:
            return Response({'detail': 'Debe estar en papelera para eliminar'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrSuperAdmin])
    def resumen(self, request):
        """Conteos por estado + papelera para la barra de resumen del admin."""
        base = Pedido.objects.all()
        estados = [
            'iniciado', 'pendiente', 'pagado', 'confirmado',
            'enviado', 'fallido', 'cancelado', 'en_disputa', 'contracargo',
        ]
        conteos = (
            base.filter(papelera=False)
            .values('estado')
            .annotate(total=Count('id'))
        )
        por_estado = {row['estado']: row['total'] for row in conteos}
        total_activos = sum(por_estado.values())
        papelera = base.filter(papelera=True).count()
        resultado = {
            'todos': total_activos,
            'papelera': papelera,
            'estados': {e: por_estado.get(e, 0) for e in estados},
        }
        return Response(resultado)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrSuperAdmin])
    def estadisticas(self, request):
        """Dashboard de estadísticas: ingresos, pedidos, top productos y categorías."""
        hoy = timezone.now().date()
        desde_str = request.query_params.get('desde')
        hasta_str = request.query_params.get('hasta')

        desde = parse_date(desde_str) if desde_str else hoy - datetime.timedelta(days=29)
        hasta = parse_date(hasta_str) if hasta_str else hoy

        # Estados que generan ingresos
        ESTADOS_VENTA = ['pagado', 'confirmado', 'enviado']

        qs = Pedido.objects.filter(
            estado__in=ESTADOS_VENTA,
            papelera=False,
            creado__date__gte=desde,
            creado__date__lte=hasta,
        )

        # Métricas del período actual
        agg = qs.aggregate(
            ventas_totales=Sum('total'),
            ventas_netas=Sum('subtotal'),
            envio_total=Sum('costo_envio'),
            descuento_total=Sum('descuento'),
            total_pedidos=Count('id'),
        )
        ventas_totales = float(agg['ventas_totales'] or 0)
        ventas_netas = float(agg['ventas_netas'] or 0)
        envio_total = float(agg['envio_total'] or 0)
        total_pedidos = agg['total_pedidos'] or 0
        valor_promedio = round(ventas_totales / total_pedidos, 2) if total_pedidos else 0
        productos_vendidos = PedidoItem.objects.filter(pedido__in=qs).aggregate(t=Sum('cantidad'))['t'] or 0

        # Período anterior (mismo número de días)
        delta = (hasta - desde).days + 1
        desde_ant = desde - datetime.timedelta(days=delta)
        hasta_ant = desde - datetime.timedelta(days=1)
        qs_ant = Pedido.objects.filter(
            estado__in=ESTADOS_VENTA,
            papelera=False,
            creado__date__gte=desde_ant,
            creado__date__lte=hasta_ant,
        )
        agg_ant = qs_ant.aggregate(
            ventas_totales=Sum('total'),
            ventas_netas=Sum('subtotal'),
            envio_total=Sum('costo_envio'),
            total_pedidos=Count('id'),
        )
        vt_ant = float(agg_ant['ventas_totales'] or 0)
        vn_ant = float(agg_ant['ventas_netas'] or 0)
        env_ant = float(agg_ant['envio_total'] or 0)
        tp_ant = agg_ant['total_pedidos'] or 0
        vp_ant = round(vt_ant / tp_ant, 2) if tp_ant else 0
        pv_ant = PedidoItem.objects.filter(pedido__in=qs_ant).aggregate(t=Sum('cantidad'))['t'] or 0

        def pct(nuevo, viejo):
            if viejo == 0:
                return None
            return round((nuevo - viejo) / viejo * 100)

        # Por día
        por_dia = list(
            qs.annotate(fecha=TruncDate('creado'))
            .values('fecha')
            .annotate(ventas=Sum('total'), pedidos=Count('id'))
            .order_by('fecha')
            .values('fecha', 'ventas', 'pedidos')
        )
        for row in por_dia:
            row['fecha'] = str(row['fecha'])
            row['ventas'] = float(row['ventas'] or 0)

        # Top productos
        top_productos = list(
            PedidoItem.objects.filter(pedido__in=qs)
            .values(nombre=F('producto__nombre'), slug=F('producto__slug'))
            .annotate(articulos=Sum('cantidad'), ventas_netas=Sum('subtotal'))
            .order_by('-articulos')[:10]
            .values('nombre', 'slug', 'articulos', 'ventas_netas')
        )
        for row in top_productos:
            row['ventas_netas'] = float(row['ventas_netas'] or 0)

        # Top categorías (usando category_ai_main como campo plano)
        top_categorias = list(
            PedidoItem.objects.filter(pedido__in=qs)
            .exclude(producto__category_ai_main='')
            .exclude(producto__category_ai_main__isnull=True)
            .values(nombre=F('producto__category_ai_main'))
            .annotate(articulos=Sum('cantidad'), ventas_netas=Sum('subtotal'))
            .order_by('-articulos')[:10]
            .values('nombre', 'articulos', 'ventas_netas')
        )
        for row in top_categorias:
            row['ventas_netas'] = float(row['ventas_netas'] or 0)

        return Response({
            'periodo': {'desde': str(desde), 'hasta': str(hasta)},
            'metricas': {
                'ventas_totales': ventas_totales,
                'ventas_netas': ventas_netas,
                'envio_total': envio_total,
                'total_pedidos': total_pedidos,
                'valor_promedio': valor_promedio,
                'productos_vendidos': int(productos_vendidos),
            },
            'vs_anterior': {
                'ventas_totales': pct(ventas_totales, vt_ant),
                'ventas_netas': pct(ventas_netas, vn_ant),
                'envio_total': pct(envio_total, env_ant),
                'total_pedidos': pct(total_pedidos, tp_ant),
                'valor_promedio': pct(valor_promedio, vp_ant),
                'productos_vendidos': pct(int(productos_vendidos), int(pv_ant)),
            },
            'por_dia': por_dia,
            'top_productos': top_productos,
            'top_categorias': top_categorias,
        })


class ClienteSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]

    def get(self, request, user_id=None):
        email = request.query_params.get('email')
        if user_id:
            qs = Pedido.objects.filter(user_id=user_id)
        elif email:
            qs = Pedido.objects.filter(direccion__email=email)
        else:
            return Response({'detail': 'user_id o email requerido'}, status=status.HTTP_400_BAD_REQUEST)
        agg = qs.aggregate(total_spent=Sum('total'))
        orders_count = qs.count()
        total_spent = agg['total_spent'] or 0
        avg_ticket = total_spent / orders_count if orders_count else 0
        return Response({
            'orders_count': orders_count,
            'total_spent': f"{total_spent:.2f}",
            'avg_ticket': f"{avg_ticket:.2f}"
        })
