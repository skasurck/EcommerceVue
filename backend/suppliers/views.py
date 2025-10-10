import logging

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from productos.models import Producto
from suppliers.management.commands.sync_supermex import (
    create_or_update_producto_from_supplier,
)
from suppliers.models import SupplierProduct
from suppliers.scraper_supermex import get_client, plp_collect_all, upsert_product
from suppliers.serializers import (
    SupplierProductSerializer,
    SupermexRunRequestSerializer,
)
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

        start_url = data.get('start_url')
        product_urls = data.get('product_urls')
        limit = data.get('limit') or 0
        max_pages = data.get('max_pages')
        sleep_s = data.get('sleep_s')
        apply_updates = data.get('apply_updates', True)
        http2 = data.get('http2', True)

        try:
            if product_urls:
                collected_urls = product_urls[:limit or None]
            else:
                with get_client(http2=http2) as client:
                    collected_urls = plp_collect_all(
                        client,
                        start_url,
                        limit=limit,
                        sleep_s=sleep_s,
                        max_pages=max_pages,
                    )
        except Exception as exc:  # pragma: no cover - logs for debugging only
            logger.exception("No se pudo recolectar URLs desde Supermex: %s", exc)
            return Response(
                {"detail": f"No se pudo recolectar URLs: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        processed_count = 0

        for url in collected_urls:
            entry = {"url": url}
            if apply_updates:
                try:
                    supplier_product = upsert_product(url)
                    pre_existing = Producto.objects.filter(
                        sku=supplier_product.supplier_sku
                    ).exists()
                    django_product = create_or_update_producto_from_supplier(
                        supplier_product
                    )

                    entry["status"] = "ok"
                    entry["product"] = SupplierProductSerializer(
                        supplier_product
                    ).data
                    if django_product:
                        was_created = not pre_existing
                        entry["django_product"] = {
                            "id": django_product.id,
                            "sku": django_product.sku,
                            "nombre": django_product.nombre,
                            "created": was_created,
                            "action": "created" if was_created else "updated",
                        }
                    else:
                        entry["django_product"] = None
                        entry["note"] = (
                            "Supplier sin precio: no se creó/actualizó Producto en Django."
                        )
                    processed_count += 1
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.exception("Error al importar %s: %s", url, exc)
                    entry["status"] = "error"
                    entry["error"] = str(exc)
            else:
                entry["status"] = "skipped"
            results.append(entry)

        response_payload = {
            "collected_count": len(collected_urls),
            "processed_count": processed_count,
            "results": results,
            "params": {
                "start_url": start_url,
                "limit": limit,
                "max_pages": max_pages,
                "sleep_s": sleep_s,
                "apply_updates": apply_updates,
                "http2": http2,
                "product_urls": product_urls,
            },
        }

        return Response(response_payload, status=status.HTTP_200_OK)


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
