"""
Lógica de negocio para productos destacados.

Flujo:
1. Filtrar productos elegibles (condiciones mínimas de calidad).
2. Separar manuales y automáticos.
3. Ordenar manuales por prioridad y excluir vencidos.
4. Calcular puntaje de candidatos automáticos.
5. Llenar la lista: primero manuales, luego automáticos hasta el límite.
"""

import logging
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

LIMITE_DESTACADOS_DEFAULT = 12


# ──────────── Elegibilidad ────────────

def _qs_elegibles_base():
    """
    Queryset base de productos que cumplen las condiciones mínimas para
    poder aparecer como destacados (manual o automático).
    """
    from .models import Producto
    return Producto.objects.filter(
        estado='publicado',
        visibilidad=True,
        disponible=True,
        stock__gt=0,
        estado_inventario='en_existencia',
    ).exclude(
        Q(imagen_principal__isnull=True) | Q(imagen_principal='')
    )


# ──────────── Scoring automático ────────────

def calcular_puntaje(producto):
    """
    Calcula el puntaje de un producto para el algoritmo automático.
    Señales consideradas: ventas recientes, novedad, oferta activa, stock, contenido.
    Retorna float >= 0.
    """
    ahora = timezone.now()
    hace_30_dias = ahora - timedelta(days=30)
    hace_7_dias = ahora - timedelta(days=7)
    puntaje = 0.0

    # — Ventas recientes (últimos 30 días) —
    try:
        from pedidos.models import PedidoItem
        ventas = PedidoItem.objects.filter(
            producto=producto,
            pedido__creado__gte=hace_30_dias,
        ).count()
        puntaje += min(ventas * 2.0, 20.0)  # máx 20 pts
    except Exception:
        logger.debug("No se pudo calcular ventas recientes para producto %s", producto.pk)

    # — Novedad (creado en últimos 7 días) —
    if producto.fecha_creacion >= hace_7_dias:
        puntaje += 15.0

    # — Oferta activa (precio rebajado directo) —
    if producto.precio_rebajado and producto.precio_rebajado > 0:
        puntaje += 10.0
    else:
        # Verificar si tiene oferta diaria vía proveedor
        try:
            from suppliers.models import ProductSupplierMap, SupplierProduct
            from promotions.models import DailyOffer
            skus = list(
                ProductSupplierMap.objects
                .filter(product=producto)
                .values_list('supplier_sku', flat=True)
            )
            if skus:
                tiene_oferta_diaria = DailyOffer.objects.filter(
                    product__supplier_sku__in=skus,
                    is_active=True,
                    start_date__lte=ahora,
                    end_date__gte=ahora,
                ).exists()
                if tiene_oferta_diaria:
                    puntaje += 10.0
        except Exception:
            logger.debug("No se pudo verificar oferta diaria para producto %s", producto.pk)

    # — Stock disponible —
    if producto.stock >= 10:
        puntaje += 5.0
    elif producto.stock >= 3:
        puntaje += 2.0

    # — Calidad de contenido —
    if producto.miniatura:
        puntaje += 2.0
    if producto.descripcion_corta:
        puntaje += 1.0
    if producto.descripcion_larga:
        puntaje += 1.0

    return puntaje


def _determinar_motivo(producto, puntaje, ahora):
    """Determina el motivo principal del destacado automático."""
    hace_7_dias = ahora - timedelta(days=7)
    if producto.fecha_creacion >= hace_7_dias:
        return 'novedad'
    if producto.precio_rebajado and producto.precio_rebajado > 0:
        return 'oferta'
    return 'ventas'


# ──────────── Lectura de destacados ────────────

def get_destacados(limite=LIMITE_DESTACADOS_DEFAULT):
    """
    Retorna la lista final de ProductoDestacado ordenada:
    1. Manuales activos y vigentes, ordenados por prioridad.
       Filtro relajado: solo requieren stock > 0 e imagen principal.
    2. Automáticos activos, ordenados por puntaje descendente.
       Filtro estricto: estado=publicado, visible, disponible, stock, imagen.
    Total máximo: `limite` registros.
    """
    from .models import ProductoDestacado
    ahora = timezone.now()

    vigencia_q = (
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=ahora)
    ) & (
        Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=ahora)
    )

    # Condiciones mínimas para manuales (stock e imagen)
    manual_q = Q(
        producto__stock__gt=0,
        producto__estado_inventario='en_existencia',
    ) & Q(producto__imagen_principal__isnull=False) & ~Q(producto__imagen_principal='')

    # Condiciones estrictas para automáticos
    auto_q = manual_q & Q(
        producto__estado='publicado',
        producto__visibilidad=True,
        producto__disponible=True,
    )

    prefetch = ('producto__categorias', 'producto__atributos__atributo')

    manuales = list(
        ProductoDestacado.objects
        .filter(activo=True, tipo='manual')
        .filter(vigencia_q)
        .filter(manual_q)
        .select_related('producto')
        .prefetch_related(*prefetch)
        .order_by('prioridad', 'id')[:limite]
    )
    ids_manuales = {d.producto_id for d in manuales}
    espacios = limite - len(manuales)

    automaticos = []
    if espacios > 0:
        automaticos = list(
            ProductoDestacado.objects
            .filter(activo=True, tipo='automatico')
            .filter(vigencia_q)
            .filter(auto_q)
            .exclude(producto_id__in=ids_manuales)
            .select_related('producto')
            .prefetch_related(*prefetch)
            .order_by('-puntaje_auto', 'id')[:espacios]
        )

    return manuales + automaticos


# ──────────── Actualización automática ────────────

def actualizar_destacados_automaticos(limite=LIMITE_DESTACADOS_DEFAULT):
    """
    Recalcula los productos destacados automáticos.
    - No modifica registros con tipo='manual'.
    - No modifica registros con bloqueado=True.
    - Crea o actualiza registros de tipo='automatico' para los mejores candidatos.
    - Desactiva los que ya no están en el top.
    """
    from .models import ProductoDestacado
    ahora = timezone.now()

    # Cuántos manuales activos y vigentes hay
    vigencia_q = (
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=ahora)
    ) & (
        Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=ahora)
    )
    manuales_activos = ProductoDestacado.objects.filter(
        tipo='manual', activo=True
    ).filter(vigencia_q).count()

    espacios_auto = max(0, limite - manuales_activos)

    if espacios_auto == 0:
        ProductoDestacado.objects.filter(
            tipo='automatico', bloqueado=False
        ).update(activo=False)
        logger.info("Destacados automáticos desactivados (sin espacios disponibles).")
        return

    # IDs que no debemos tocar
    no_tocar_ids = set(
        ProductoDestacado.objects.filter(
            Q(tipo='manual') | Q(bloqueado=True)
        ).values_list('producto_id', flat=True)
    )

    elegibles = _qs_elegibles_base().exclude(id__in=no_tocar_ids)

    # Calcular puntajes
    candidatos = []
    for producto in elegibles.only(
        'id', 'nombre', 'precio_rebajado', 'miniatura', 'imagen_principal',
        'descripcion_corta', 'descripcion_larga', 'stock', 'fecha_creacion',
    ):
        try:
            puntaje = calcular_puntaje(producto)
            if puntaje > 0:
                candidatos.append((producto, puntaje))
        except Exception:
            logger.exception("Error calculando puntaje de producto %s", producto.pk)

    candidatos.sort(key=lambda x: x[1], reverse=True)
    top = candidatos[:espacios_auto]
    top_ids = {p.id for p, _ in top}

    # Desactivar los que ya no están en el top
    desactivados = ProductoDestacado.objects.filter(
        tipo='automatico', bloqueado=False
    ).exclude(producto_id__in=top_ids).update(activo=False)

    # Crear o actualizar
    creados = actualizados = 0
    for producto, puntaje in top:
        motivo = _determinar_motivo(producto, puntaje, ahora)
        _, created = ProductoDestacado.objects.update_or_create(
            producto=producto,
            defaults={
                'tipo': 'automatico',
                'activo': True,
                'puntaje_auto': round(puntaje, 4),
                'motivo': motivo,
            },
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    logger.info(
        "Destacados automáticos: %d creados, %d actualizados, %d desactivados.",
        creados, actualizados, desactivados,
    )
