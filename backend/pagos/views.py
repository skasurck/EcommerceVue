import logging
import mercadopago
import hashlib
import hmac
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pedidos.models import Pedido
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def _get_mp_token():
    """
    Retorna el token correcto según la variable MP_TEST_MODE o DEBUG.
    Permite usar credenciales de prueba en el servidor de producción
    simplemente poniendo MP_TEST_MODE=true en el .env.
    """
    test_mode = getattr(settings, 'MP_TEST_MODE', settings.DEBUG)
    # MP_TEST_MODE puede llegar como string "true"/"false" desde el .env
    if isinstance(test_mode, str):
        test_mode = test_mode.lower() in ('true', '1', 'yes')
    token = settings.MP_ACCESS_TOKEN_TEST if test_mode else settings.MP_ACCESS_TOKEN
    # Fallback: si el token seleccionado está vacío, intentar el otro
    if not token:
        token = settings.MP_ACCESS_TOKEN or settings.MP_ACCESS_TOKEN_TEST
    return token


def _verify_mp_signature(request) -> bool:
    """
    Verifica la firma del webhook de Mercado Pago usando HMAC-SHA256.
    Retorna True si la firma es válida o si no hay secreto configurado (dev).
    Docs: https://www.mercadopago.com.mx/developers/es/docs/your-integrations/notifications/webhooks
    """
    secret = getattr(settings, "MP_WEBHOOK_SECRET", "")
    if not secret:
        # Sin secreto configurado: solo permitir en desarrollo
        return bool(settings.DEBUG)

    x_signature = request.META.get("HTTP_X_SIGNATURE", "")
    x_request_id = request.META.get("HTTP_X_REQUEST_ID", "")
    data_id = request.query_params.get("data.id", "")

    # Parsear ts y v1 del header x-signature
    ts = ""
    v1 = ""
    for part in x_signature.split(","):
        key, _, value = part.partition("=")
        if key.strip() == "ts":
            ts = value.strip()
        elif key.strip() == "v1":
            v1 = value.strip()

    if not ts or not v1:
        return False

    # Construir el mensaje a firmar
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    expected = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


class MercadoPagoWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not _verify_mp_signature(request):
            return Response({"detail": "Firma inválida"}, status=status.HTTP_400_BAD_REQUEST)

        notification = request.data
        sdk = mercadopago.SDK(_get_mp_token())

        # Obtener el payment_id según el formato del evento
        # Nuevo formato Webhooks: {"type": "payment", "action": "payment.updated", "data": {"id": "123"}}
        # Formato IPN legacy:     {"topic": "payment", "resource": "/v1/payments/123"}
        payment_id = None

        notif_type = notification.get('type') or notification.get('topic', '')
        if notif_type == 'payment':
            data = notification.get('data') or {}
            # Nuevo formato
            payment_id = data.get('id') or request.query_params.get('data.id')
            # IPN legacy: resource puede ser "/v1/payments/123" o solo "123"
            if not payment_id:
                resource = notification.get('resource', '')
                payment_id = str(resource).split('/')[-1] if resource else None

        if not payment_id:
            # Evento no relevante (merchant_order, etc.) → responder 200 de todos modos
            return Response(status=status.HTTP_200_OK)

        try:
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info.get("response", {})

            if payment.get('status') == 'approved':
                external_reference = payment.get('external_reference')
                if external_reference:
                    try:
                        pedido = Pedido.objects.get(id=external_reference)
                        if pedido.estado != 'pagado':
                            pedido.estado = 'pagado'
                            pedido.mercadopago_payment_id = str(payment.get('id', ''))
                            pedido.save()
                            logger.info("Pedido %s marcado como pagado via MP payment %s.", external_reference, payment_id)
                    except Pedido.DoesNotExist:
                        logger.warning("Webhook MP: pedido con external_reference=%s no encontrado.", external_reference)
        except Exception as e:
            logger.exception("Error procesando webhook de Mercado Pago (payment_id=%s): %s", payment_id, e)

        return Response(status=status.HTTP_200_OK)


class MercadoPagoPreferenceView(APIView):
    def post(self, request, *args, **kwargs):
        sdk = mercadopago.SDK(_get_mp_token())

        cart_items = request.data.get('items', [])
        external_reference = request.data.get('external_reference')  # ID del pedido

        if not cart_items:
            return Response({"error": "El carrito está vacío"}, status=status.HTTP_400_BAD_REQUEST)

        if not external_reference:
            return Response({"error": "Falta la referencia externa (ID de pedido)"}, status=status.HTTP_400_BAD_REQUEST)

        items = []
        for cart_item in cart_items:
            producto = cart_item.get('producto', {})
            cantidad = cart_item.get('cantidad', 0)

            precio_rebajado = producto.get('precio_rebajado')
            precio_normal = producto.get('precio_normal')

            if precio_rebajado is not None:
                precio = precio_rebajado
            else:
                precio = precio_normal

            if not all([producto.get('nombre'), cantidad, precio is not None]):
                continue

            items.append({
                "title": producto.get('nombre'),
                "quantity": cantidad,
                "unit_price": float(precio),
                "currency_id": "MXN"
            })

        if not items:
            return Response({"error": "No hay items válidos en el carrito"}, status=status.HTTP_400_BAD_REQUEST)

        request_back_urls = request.data.get('back_urls') or {}
        frontend_base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
        success_url = request.data.get('success_url') or request_back_urls.get('success') or f"{frontend_base_url}/gracias"
        failure_url = request.data.get('failure_url') or request_back_urls.get('failure') or f"{frontend_base_url}/checkout/fallo"
        pending_url = request.data.get('pending_url') or request_back_urls.get('pending') or f"{frontend_base_url}/checkout/pendiente"

        back_urls = {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url
        }

        if not back_urls["success"]:
            return Response(
                {"error": "No se proporcionó la URL de success requerida por Mercado Pago."},
                status=status.HTTP_400_BAD_REQUEST
            )

        preference_data = {
            "items": items,
            "back_urls": back_urls,
            "external_reference": external_reference,
        }

        requested_auto_return = request.data.get("auto_return", "approved")
        success_callback = back_urls.get("success")
        if requested_auto_return and success_callback and success_callback.startswith("https://"):
            preference_data["auto_return"] = requested_auto_return

        try:
            preference_response = sdk.preference().create(preference_data)
            logger.debug("Mercado Pago API Response: %s", preference_response)

            response_status = preference_response.get("status")
            preference = preference_response.get("response", {}) or {}

            if response_status and response_status >= 400:
                error_message = preference.get("message") or "Mercado Pago rechazó la solicitud"
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            preference_id = preference.get("id")
            init_point = preference.get("sandbox_init_point") or preference.get("init_point")

            if not preference_id or not init_point:
                return Response(
                    {"error": "Mercado Pago no regresó la información esperada."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            try:
                pedido = Pedido.objects.get(id=external_reference)
                pedido.mercadopago_preference_id = preference_id
                pedido.save()
            except Pedido.DoesNotExist:
                logger.warning("ADVERTENCIA: No se encontró el pedido con ID %s para guardar el preference_id.", external_reference)

            return Response({
                "preference_id": preference_id,
                "init_point": init_point
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error al crear preferencia de Mercado Pago: %s", e)
            return Response({"error": "Hubo un problema al comunicarse con Mercado Pago."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
