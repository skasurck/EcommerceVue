from rest_framework.response import Response
from suppliers.models import SupplierProduct
from suppliers.utils import effective_qty

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
