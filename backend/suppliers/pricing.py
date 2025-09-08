# suppliers/pricing.py
from decimal import Decimal, ROUND_UP

def apply_markup(price_supplier: Decimal, margin=Decimal("0.15"), step=Decimal("10")):
    base = price_supplier * (Decimal("1.0") + margin)
    # Redondeo hacia arriba al múltiplo más cercano de `step` (ej. $10)
    return (base / step).to_integral_value(rounding=ROUND_UP) * step
