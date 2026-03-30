import logging
from datetime import timedelta

from celery.result import AsyncResult
from django.db.models import Q, Sum, Case, When, IntegerField, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from suppliers.models import SupplierProduct, SupplierStockHistory
from suppliers.serializers import (
    SupplierProductSerializer,
    SupermexRunRequestSerializer,
)
from suppliers.tasks import run_supermex_scraper, run_supermex_stock_sync
from suppliers.utils import effective_qty


logger = logging.getLogger(__name__)

def supplier_status(request, sku):
    try:
        sp = SupplierProduct.objects.get(supplier_sku=sku)
    except SupplierProduct.DoesNotExist:
        return Response({"found": False}, status=404)

    qty_eff = effective_qty(sp.available_qty, sp.in_stock)
    is_virtual = not (sp.available_qty and sp.available_qty > 0)

    return Response({
        "found": True,
        "in_stock": sp.in_stock,
        "available_qty": sp.available_qty or 0,   # real, si hay
        "effective_qty": qty_eff,                 # lo que debe usar el front
        "is_virtual_qty": is_virtual,             # bandera para UI
        "price_supplier": str(sp.price_supplier),
    })


class SupermexRunView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = SupermexRunRequestSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        task = run_supermex_scraper.delay(
            start_url=data.get('start_url'),
            product_urls=data.get('product_urls'),
            limit=data.get('limit') or 0,
            max_pages=data.get('max_pages'),
            sleep_s=data.get('sleep_s'),
            apply_updates=data.get('apply_updates', True),
            http2=data.get('http2', True),
        )

        return Response({'task_id': task.id, 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class SupermexTaskStatusView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            data = {'state': 'PENDING', 'current': 0, 'total': 0, 'status': 'En cola...'}
        elif result.state == 'PROGRESS':
            data = {'state': 'PROGRESS', **result.info}
        elif result.state == 'SUCCESS':
            data = {'state': 'SUCCESS', **result.result}
        else:
            data = {'state': result.state, 'status': str(result.info)}
        return Response(data)


class SupermexStockSyncView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        http2 = request.data.get('http2', True)
        sleep_s = request.data.get('sleep_s', 0.3)
        task = run_supermex_stock_sync.delay(http2=http2, sleep_s=sleep_s)
        return Response({'task_id': task.id, 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)


class SupermexLatestProductsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 50))
        except (TypeError, ValueError):
            limit = 50
        limit = max(1, min(limit, 200))

        search = (request.query_params.get('search') or '').strip()

        queryset = SupplierProduct.objects.filter(supplier='supermex')
        if search:
            queryset = queryset.filter(
                Q(supplier_sku__icontains=search) | Q(name__icontains=search)
            )

        queryset = queryset.order_by('-last_seen')[:limit]
        serializer = SupplierProductSerializer(queryset, many=True)
        return Response(serializer.data)


class SupermexSalesStatsView(APIView):
    """
    Estadísticas de ventas estimadas a partir de descensos de stock.
    Un descenso de qty entre dos snapshots consecutivos = unidades vendidas.

    GET /suppliers/supermex/sales-stats/?days=30&top=20
      - days: ventana de análisis (default 30)
      - top: cuántos productos devolver en el ranking (default 20)

    GET /suppliers/supermex/sales-stats/?sku=XXXXX&days=30
      - Devuelve la serie histórica diaria de un producto concreto
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            days = max(1, int(request.query_params.get('days', 30)))
        except (TypeError, ValueError):
            days = 30
        try:
            top = max(1, min(int(request.query_params.get('top', 20)), 100))
        except (TypeError, ValueError):
            top = 20

        since = timezone.now() - timedelta(days=days)
        sku = (request.query_params.get('sku') or '').strip()

        # --- Serie histórica de un SKU concreto ---
        if sku:
            try:
                sp = SupplierProduct.objects.get(supplier_sku=sku, supplier='supermex')
            except SupplierProduct.DoesNotExist:
                return Response({'error': 'SKU no encontrado'}, status=404)

            snapshots = list(
                SupplierStockHistory.objects
                .filter(supplier_product=sp, recorded_at__gte=since)
                .order_by('recorded_at')
                .values('recorded_at', 'available_qty')
            )

            # Calcular ventas estimadas entre snapshots consecutivos
            series = []
            for i in range(1, len(snapshots)):
                prev = snapshots[i - 1]
                curr = snapshots[i]
                sold = max(0, prev['available_qty'] - curr['available_qty'])
                series.append({
                    'date': curr['recorded_at'].isoformat(),
                    'qty': curr['available_qty'],
                    'sold': sold,
                })

            return Response({
                'sku': sku,
                'name': sp.name,
                'days': days,
                'series': series,
                'total_sold': sum(s['sold'] for s in series),
            })

        # --- Ranking top productos por ventas estimadas ---
        # Traemos todos los snapshots del período ordenados por producto y fecha
        histories = (
            SupplierStockHistory.objects
            .filter(recorded_at__gte=since, supplier_product__supplier='supermex')
            .select_related('supplier_product')
            .order_by('supplier_product_id', 'recorded_at')
            .values('supplier_product_id', 'supplier_product__supplier_sku',
                    'supplier_product__name', 'recorded_at', 'available_qty')
        )

        # Agrupar por producto y sumar descensos
        sales_by_product = {}
        prev_by_product = {}

        for row in histories:
            pid = row['supplier_product_id']
            qty = row['available_qty']
            if pid in prev_by_product:
                diff = max(0, prev_by_product[pid] - qty)
                if pid not in sales_by_product:
                    sales_by_product[pid] = {
                        'sku': row['supplier_product__supplier_sku'],
                        'name': row['supplier_product__name'],
                        'total_sold': 0,
                        'snapshots': 0,
                    }
                sales_by_product[pid]['total_sold'] += diff
                sales_by_product[pid]['snapshots'] += 1
            prev_by_product[pid] = qty

        ranking = sorted(sales_by_product.values(), key=lambda x: x['total_sold'], reverse=True)[:top]

        return Response({
            'days': days,
            'since': since.isoformat(),
            'ranking': ranking,
        })
