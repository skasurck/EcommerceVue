import logging

from celery.result import AsyncResult
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from suppliers.models import SupplierProduct
from suppliers.serializers import (
    SupplierProductSerializer,
    SupermexRunRequestSerializer,
)
from suppliers.tasks import run_supermex_scraper
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
