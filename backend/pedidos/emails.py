"""
Tareas Celery para el envío de emails transaccionales de pedidos.

Emails implementados:
  - enviar_email_pedido_creado   → cuando se crea un pedido (estado=pendiente)
  - enviar_email_pago_confirmado → cuando el pago es aprobado (estado=pagado)
  - enviar_email_enviado         → cuando el pedido es despachado (estado=enviado)
  - enviar_email_cancelado       → cuando el pedido se cancela (estado=cancelado)
"""

import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt(n):
    try:
        return f"${float(n):,.2f} MXN"
    except (TypeError, ValueError):
        return str(n)


def _items_rows(items):
    rows = ""
    for item in items:
        nombre = getattr(item.producto, 'nombre', '—')
        rows += f"""
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;color:#111827;">{nombre}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;text-align:center;color:#374151;">{item.cantidad}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;text-align:right;color:#374151;">{_fmt(item.precio_unitario)}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #f3f4f6;text-align:right;font-weight:600;color:#111827;">{_fmt(item.subtotal)}</td>
        </tr>"""
    return rows


def _tabla_items(items):
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-collapse:collapse;margin:16px 0;font-size:14px;">
      <thead>
        <tr style="background:#f9fafb;">
          <th style="padding:8px;text-align:left;color:#6b7280;font-weight:600;border-bottom:2px solid #e5e7eb;">Producto</th>
          <th style="padding:8px;text-align:center;color:#6b7280;font-weight:600;border-bottom:2px solid #e5e7eb;">Cant.</th>
          <th style="padding:8px;text-align:right;color:#6b7280;font-weight:600;border-bottom:2px solid #e5e7eb;">Precio</th>
          <th style="padding:8px;text-align:right;color:#6b7280;font-weight:600;border-bottom:2px solid #e5e7eb;">Subtotal</th>
        </tr>
      </thead>
      <tbody>{_items_rows(items)}</tbody>
    </table>"""


def _totales(pedido):
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-collapse:collapse;font-size:14px;margin-top:8px;">
      <tr>
        <td style="padding:4px 8px;color:#6b7280;">Subtotal</td>
        <td style="padding:4px 8px;text-align:right;color:#374151;">{_fmt(pedido.subtotal)}</td>
      </tr>
      <tr>
        <td style="padding:4px 8px;color:#6b7280;">Envío ({pedido.metodo_envio.nombre})</td>
        <td style="padding:4px 8px;text-align:right;color:#374151;">{_fmt(pedido.costo_envio)}</td>
      </tr>
      <tr style="border-top:2px solid #e5e7eb;">
        <td style="padding:8px;font-weight:700;font-size:16px;color:#111827;">Total</td>
        <td style="padding:8px;text-align:right;font-weight:700;font-size:16px;color:#111827;">{_fmt(pedido.total)}</td>
      </tr>
    </table>"""


def _base_html(title, content, pedido_id=None):
    tienda = getattr(settings, 'TIENDA_NOMBRE', 'Mktska Digital')
    frontend = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')
    pedido_link = ""
    if pedido_id:
        pedido_link = f"""
        <p style="text-align:center;margin-top:24px;">
          <a href="{frontend}/mis-pedidos/{pedido_id}"
             style="display:inline-block;background:#FBBF24;color:#111827;font-weight:700;
                    padding:12px 28px;border-radius:6px;text-decoration:none;font-size:14px;">
            Ver mi pedido
          </a>
        </p>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:8px;overflow:hidden;
                    box-shadow:0 1px 3px rgba(0,0,0,.12);max-width:100%;">
        <!-- Header -->
        <tr>
          <td style="background:#111827;padding:20px 32px;">
            <span style="font-size:22px;font-weight:700;color:#FBBF24;">{tienda}</span>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:32px;">
            <h2 style="margin:0 0 20px;font-size:20px;color:#111827;">{title}</h2>
            {content}
            {pedido_link}
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f9fafb;padding:16px 32px;text-align:center;
                     border-top:1px solid #e5e7eb;">
            <p style="margin:0;font-size:12px;color:#9ca3af;">
              © 2025 {tienda}. Todos los derechos reservados.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _enviar(subject, html_body, to_email):
    """Envía un email HTML. Maneja errores sin lanzar excepción."""
    if not to_email:
        logger.warning("[email] No hay destinatario para: %s", subject)
        return
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body="Este email requiere un cliente con soporte HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        logger.info("[email] Enviado '%s' a %s", subject, to_email)
    except Exception as exc:
        logger.exception("[email] Error al enviar '%s': %s", subject, exc)
        raise  # permite que Celery reintente


# ── Tareas Celery ──────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_pedido_creado(self, pedido_id):
    """Email de confirmación cuando se crea el pedido."""
    from pedidos.models import Pedido
    try:
        pedido = Pedido.objects.select_related(
            'direccion', 'metodo_envio'
        ).prefetch_related('items__producto').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.warning("[email] Pedido #%s no encontrado", pedido_id)
        return

    dir_ = pedido.direccion
    nombre = f"{dir_.nombre} {dir_.apellidos}" if dir_ else "Cliente"
    email = dir_.email if dir_ else None

    metodo_pago_labels = {
        'transferencia': 'Transferencia directa',
        'tarjeta': 'Tarjeta de crédito/débito',
        'mercadopago': 'Mercado Pago',
    }
    metodo_label = metodo_pago_labels.get(pedido.metodo_pago, pedido.metodo_pago)

    content = f"""
    <p style="color:#374151;margin:0 0 12px;">Hola <strong>{nombre}</strong>,</p>
    <p style="color:#374151;margin:0 0 20px;">
      Recibimos tu pedido <strong>#{pedido.id}</strong>. En breve lo procesaremos.
    </p>

    <div style="background:#fef9c3;border:1px solid #fde047;border-radius:6px;
                padding:12px 16px;margin-bottom:20px;">
      <p style="margin:0;font-size:13px;color:#854d0e;">
        <strong>Estado:</strong> Pendiente de pago/confirmación &nbsp;|&nbsp;
        <strong>Método de pago:</strong> {metodo_label}
      </p>
    </div>

    <h3 style="font-size:14px;color:#6b7280;text-transform:uppercase;
               letter-spacing:.05em;margin:0 0 4px;">Productos</h3>
    {_tabla_items(pedido.items.all())}
    {_totales(pedido)}

    <div style="margin-top:24px;padding:16px;background:#f9fafb;
                border-radius:6px;font-size:13px;color:#374151;">
      <strong>Dirección de entrega:</strong><br>
      {dir_.calle} {dir_.numero_exterior}
      {(' Int. ' + dir_.numero_interior) if dir_.numero_interior else ''},
      {dir_.colonia}, {dir_.ciudad}, {dir_.estado} {dir_.codigo_postal}
    </div>
    """

    tienda = getattr(settings, 'TIENDA_NOMBRE', 'Mktska Digital')
    html = _base_html(f"Pedido recibido #{pedido.id}", content, pedido_id=pedido.id)
    try:
        _enviar(f"[{tienda}] Tu pedido #{pedido.id} fue recibido", html, email)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_pago_confirmado(self, pedido_id):
    """Email cuando el pago es aprobado."""
    from pedidos.models import Pedido
    try:
        pedido = Pedido.objects.select_related(
            'direccion', 'metodo_envio'
        ).prefetch_related('items__producto').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        return

    dir_ = pedido.direccion
    nombre = f"{dir_.nombre} {dir_.apellidos}" if dir_ else "Cliente"
    email = dir_.email if dir_ else None

    content = f"""
    <p style="color:#374151;margin:0 0 12px;">Hola <strong>{nombre}</strong>,</p>
    <p style="color:#374151;margin:0 0 20px;">
      ¡Tu pago fue confirmado! Estamos preparando tu pedido <strong>#{pedido.id}</strong>.
    </p>

    <div style="background:#dcfce7;border:1px solid #86efac;border-radius:6px;
                padding:12px 16px;margin-bottom:20px;">
      <p style="margin:0;font-size:13px;color:#166534;">
        ✓ Pago aprobado — pronto recibirás otro email cuando tu pedido sea enviado.
      </p>
    </div>

    <h3 style="font-size:14px;color:#6b7280;text-transform:uppercase;
               letter-spacing:.05em;margin:0 0 4px;">Resumen</h3>
    {_tabla_items(pedido.items.all())}
    {_totales(pedido)}
    """

    tienda = getattr(settings, 'TIENDA_NOMBRE', 'Mktska Digital')
    html = _base_html(f"¡Pago confirmado! Pedido #{pedido.id}", content, pedido_id=pedido.id)
    try:
        _enviar(f"[{tienda}] Pago confirmado — Pedido #{pedido.id}", html, email)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_enviado(self, pedido_id):
    """Email cuando el pedido es despachado."""
    from pedidos.models import Pedido
    try:
        pedido = Pedido.objects.select_related(
            'direccion', 'metodo_envio'
        ).prefetch_related('items__producto').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        return

    dir_ = pedido.direccion
    nombre = f"{dir_.nombre} {dir_.apellidos}" if dir_ else "Cliente"
    email = dir_.email if dir_ else None

    guia_block = ""
    if pedido.numero_guia:
        guia_block = f"""
    <div style="background:#fef9c3;border:1px solid #fde047;border-radius:6px;
                padding:14px 16px;margin-bottom:20px;">
      <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:#854d0e;">
        Número de guía de rastreo:
      </p>
      <p style="margin:0;font-size:20px;font-weight:700;color:#111827;
                letter-spacing:.05em;font-family:monospace;">
        {pedido.numero_guia}
      </p>
    </div>"""

    content = f"""
    <p style="color:#374151;margin:0 0 12px;">Hola <strong>{nombre}</strong>,</p>
    <p style="color:#374151;margin:0 0 20px;">
      ¡Tu pedido <strong>#{pedido.id}</strong> está en camino!
      Pronto llegará a tu dirección.
    </p>

    <div style="background:#dbeafe;border:1px solid #93c5fd;border-radius:6px;
                padding:12px 16px;margin-bottom:20px;">
      <p style="margin:0;font-size:13px;color:#1e40af;">
        🚚 Tu pedido fue enviado por <strong>{pedido.metodo_envio.nombre}</strong>.
      </p>
    </div>

    {guia_block}

    <div style="padding:16px;background:#f9fafb;border-radius:6px;
                font-size:13px;color:#374151;margin-bottom:20px;">
      <strong>Dirección de entrega:</strong><br>
      {dir_.calle} {dir_.numero_exterior}
      {(' Int. ' + dir_.numero_interior) if dir_.numero_interior else ''},
      {dir_.colonia}, {dir_.ciudad}, {dir_.estado} {dir_.codigo_postal}
    </div>

    <h3 style="font-size:14px;color:#6b7280;text-transform:uppercase;
               letter-spacing:.05em;margin:0 0 4px;">Productos enviados</h3>
    {_tabla_items(pedido.items.all())}
    """

    tienda = getattr(settings, 'TIENDA_NOMBRE', 'Mktska Digital')
    html = _base_html(f"Tu pedido #{pedido.id} está en camino 🚚", content, pedido_id=pedido.id)
    try:
        _enviar(f"[{tienda}] Tu pedido #{pedido.id} fue enviado", html, email)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_cancelado(self, pedido_id):
    """Email cuando el pedido es cancelado."""
    from pedidos.models import Pedido
    try:
        pedido = Pedido.objects.select_related(
            'direccion', 'metodo_envio'
        ).prefetch_related('items__producto').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        return

    dir_ = pedido.direccion
    nombre = f"{dir_.nombre} {dir_.apellidos}" if dir_ else "Cliente"
    email = dir_.email if dir_ else None
    frontend = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')

    content = f"""
    <p style="color:#374151;margin:0 0 12px;">Hola <strong>{nombre}</strong>,</p>
    <p style="color:#374151;margin:0 0 20px;">
      Tu pedido <strong>#{pedido.id}</strong> fue cancelado.
      Si realizaste un pago, será reembolsado en los próximos días hábiles.
    </p>

    <div style="background:#fee2e2;border:1px solid #fca5a5;border-radius:6px;
                padding:12px 16px;margin-bottom:20px;">
      <p style="margin:0;font-size:13px;color:#991b1b;">
        ✕ Pedido cancelado. Si tienes dudas, contáctanos.
      </p>
    </div>

    <p style="text-align:center;margin-top:24px;">
      <a href="{frontend}/productos"
         style="display:inline-block;background:#111827;color:#FBBF24;font-weight:700;
                padding:12px 28px;border-radius:6px;text-decoration:none;font-size:14px;">
        Seguir comprando
      </a>
    </p>
    """

    tienda = getattr(settings, 'TIENDA_NOMBRE', 'Mktska Digital')
    html = _base_html(f"Pedido #{pedido.id} cancelado", content)
    try:
        _enviar(f"[{tienda}] Tu pedido #{pedido.id} fue cancelado", html, email)
    except Exception as exc:
        raise self.retry(exc=exc)
