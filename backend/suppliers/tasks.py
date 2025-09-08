# suppliers/tasks.py (o donde tengas apply_rules)
from django.utils import timezone
from suppliers.models import SupplierProduct, ProductSupplierMap
from productos.models import Producto
from suppliers.utils import effective_qty
from decimal import Decimal

MARKUP = Decimal("1.15")  # tu +15%

def apply_rules():
    links = ProductSupplierMap.objects.select_related("product").all()
    for link in links:
        p: Producto = link.product
        try:
            sp = SupplierProduct.objects.get(supplier_sku=link.supplier_sku)
        except SupplierProduct.DoesNotExist:
            continue

        qty_eff = effective_qty(sp.available_qty, sp.in_stock)

        # 1) Stock / estado inventario / visibilidad
        if qty_eff > 0:
            # En existencia
            p.estado_inventario = "en_existencia"
            p.disponible = True
            p.visibilidad = True
            # solo sube stock si lo tienes en 0 o menor que el mínimo virtual (evita inflar si ya tienes real)
            if p.stock == 0 or p.stock < qty_eff:
                p.stock = qty_eff
        else:
            # Agotado
            p.estado_inventario = "agotado"
            # Si quisieras ocultar al quedar agotado:
            if getattr(link, "auto_hide_when_oos", True):
                p.visibilidad = False
            p.disponible = False
            # opcional: no toques p.stock para conservar histórico

        # 2) Precios (aplicar +15% sobre price_supplier, si viene > 0)
        if sp.price_supplier and sp.price_supplier > 0:
            base = sp.price_supplier
            precio_nuevo = (base * MARKUP).quantize(Decimal("0.01"))
            p.precio_normal = precio_nuevo
            # si manejas rebajado aparte, decide tu lógica aquí

        p.save(update_fields=[
            "estado_inventario", "disponible", "visibilidad",
            "stock", "precio_normal"
        ])
    