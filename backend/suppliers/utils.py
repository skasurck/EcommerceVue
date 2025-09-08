# suppliers/utils.py
from django.conf import settings

def effective_qty(available_qty: int | None, in_stock: bool) -> int:
    if not in_stock:
        return 0
    if available_qty and available_qty > 0:
        return available_qty
    return getattr(settings, "SUPPLIER_MIN_VIRTUAL_QTY", 1)
