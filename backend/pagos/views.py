import logging
import mercadopago
import hashlib
import hmac
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pedidos.models import Pedido
from pagos.models import ConfiguracionTransferencia
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
        # Sin secreto configurado: acepta el webhook pero lo registra como advertencia
        logger.warning("MP_WEBHOOK_SECRET no configurado — webhook aceptado sin validar firma.")
        return True

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

        notif_type = notification.get('type') or notification.get('topic', '')
        data = notification.get('data') or {}
        event_id = data.get('id') or request.query_params.get('data.id')

        # ── Contracargo ──────────────────────────────────────────────────────
        if notif_type == 'chargebacks':
            try:
                pedido = Pedido.objects.get(mercadopago_payment_id=str(event_id)) if event_id else None
                if pedido:
                    pedido.estado = 'contracargo'
                    pedido.save(update_fields=['estado'])
                    logger.critical(
                        "CONTRACARGO recibido: pedido #%s, chargeback_id=%s",
                        pedido.id, event_id,
                    )
                else:
                    logger.critical("CONTRACARGO recibido pero pedido no encontrado: chargeback_id=%s", event_id)
            except Exception as e:
                logger.exception("Error procesando contracargo (id=%s): %s", event_id, e)
            return Response(status=status.HTTP_200_OK)

        # ── Pago (aprobado, fraude, disputa) ─────────────────────────────────
        payment_id = None
        if notif_type == 'payment':
            payment_id = event_id
            if not payment_id:
                resource = notification.get('resource', '')
                payment_id = str(resource).split('/')[-1] if resource else None

        if not payment_id:
            return Response(status=status.HTTP_200_OK)

        try:
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info.get("response", {})
            pay_status = payment.get('status', '')
            pay_detail = payment.get('status_detail', '')
            external_reference = payment.get('external_reference')

            # Fraudes: status_detail con indicadores de fraude o acción de alerta
            FRAUD_DETAILS = {
                'cc_rejected_blacklist', 'cc_rejected_fraud',
                'fraud_risk_detected', 'risk_alert',
            }
            is_fraud = (
                pay_detail in FRAUD_DETAILS
                or notification.get('action', '') in ('risk_alert', 'payment.fraud_risk')
            )

            if external_reference:
                try:
                    pedido = Pedido.objects.get(id=external_reference)

                    if is_fraud:
                        pedido.estado = 'en_disputa'
                        pedido.save(update_fields=['estado'])
                        logger.critical(
                            "ALERTA DE FRAUDE: pedido #%s, payment_id=%s, detail=%s",
                            pedido.id, payment_id, pay_detail,
                        )

                    elif pay_status == 'approved' and pedido.estado != 'pagado':
                        pedido.estado = 'pagado'
                        pedido.mercadopago_payment_id = str(payment.get('id', ''))
                        pedido.save(update_fields=['estado', 'mercadopago_payment_id'])
                        logger.info(
                            "Pedido #%s marcado como pagado via MP payment %s.",
                            pedido.id, payment_id,
                        )

                    elif pay_status == 'in_mediation' and pedido.estado != 'en_disputa':
                        pedido.estado = 'en_disputa'
                        pedido.save(update_fields=['estado'])
                        logger.warning(
                            "Pedido #%s en mediación (disputa), payment_id=%s.",
                            pedido.id, payment_id,
                        )

                except Pedido.DoesNotExist:
                    logger.warning(
                        "Webhook MP: pedido con external_reference=%s no encontrado (payment_id=%s).",
                        external_reference, payment_id,
                    )
        except Exception as e:
            logger.exception("Error procesando webhook de Mercado Pago (payment_id=%s): %s", payment_id, e)

        return Response(status=status.HTTP_200_OK)


class MercadoPagoPreferenceView(APIView):
    permission_classes = [permissions.AllowAny]

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

        frontend_base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")

        def _safe_url(path):
            """Construye una URL segura ignorando cualquier URL del cliente."""
            return f"{frontend_base_url}{path}"

        success_url = _safe_url("/gracias")
        failure_url = _safe_url("/checkout/fallo")
        pending_url = _safe_url("/checkout/pendiente")

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

        # Agregar datos del comprador — requerido por MP para habilitar pagos en efectivo (OXXO, etc.)
        try:
            pedido = Pedido.objects.select_related('direccion', 'user').get(id=external_reference)
            dir_ = pedido.direccion
            payer_email = (dir_.email if dir_ else None) or (pedido.user.email if pedido.user else None)
            if payer_email:
                payer = {"email": payer_email}
                if dir_:
                    if dir_.nombre:
                        payer["first_name"] = dir_.nombre
                    if dir_.apellidos:
                        payer["last_name"] = dir_.apellidos
                    if dir_.telefono:
                        payer["phone"] = {"number": dir_.telefono}
                preference_data["payer"] = payer
                logger.info("MP payer data: %s", payer)
        except Pedido.DoesNotExist:
            pass

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
            test_mode = getattr(settings, 'MP_TEST_MODE', settings.DEBUG)
            if isinstance(test_mode, str):
                test_mode = test_mode.lower() in ('true', '1', 'yes')
            if test_mode:
                init_point = preference.get("sandbox_init_point") or preference.get("init_point")
            else:
                init_point = preference.get("init_point")

            if not preference_id or not init_point:
                return Response(
                    {"error": "Mercado Pago no regresó la información esperada."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            try:
                _pedido = Pedido.objects.get(id=external_reference)
                _pedido.mercadopago_preference_id = preference_id
                _pedido.save()
            except Pedido.DoesNotExist:
                logger.warning("ADVERTENCIA: No se encontró el pedido con ID %s para guardar el preference_id.", external_reference)

            return Response({
                "preference_id": preference_id,
                "init_point": init_point
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error al crear preferencia de Mercado Pago: %s", e)
            return Response({"error": "Hubo un problema al comunicarse con Mercado Pago."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


TRANSFERENCIA_FIELDS = ['banco', 'clabe', 'numero_cuenta', 'beneficiario', 'instrucciones', 'activa']


class ConfiguracionTransferenciaView(APIView):
    """
    GET  — público, para el checkout.
    PUT  — solo admin/super_admin.
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        cfg = ConfiguracionTransferencia.get()
        return Response({f: getattr(cfg, f) for f in TRANSFERENCIA_FIELDS})

    def put(self, request):
        if not request.user.is_staff and not getattr(request.user, 'rol', '') in ('admin', 'super_admin'):
            return Response({'detail': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        cfg = ConfiguracionTransferencia.get()
        for field in TRANSFERENCIA_FIELDS:
            if field in request.data:
                setattr(cfg, field, request.data[field])
        cfg.save()
        return Response({f: getattr(cfg, f) for f in TRANSFERENCIA_FIELDS})
