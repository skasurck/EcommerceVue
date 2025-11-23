import mercadopago
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pedidos.models import Pedido
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class MercadoPagoWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        notification = request.data
        topic = notification.get('topic')
        resource_id = notification.get('resource')

        # Para producción, es vital verificar la autenticidad del webhook
        # usando el x-signature header.

        if topic == 'merchant_order':
            # Lógica para 'merchant_order' si se usa
            pass
        elif topic == 'payment' and resource_id:
            try:
                sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN_TEST)
                payment_info = sdk.payment().get(resource_id)
                payment = payment_info.get("response")

                if payment and payment.get('status') == 'approved':
                    external_reference = payment.get('external_reference')
                    if external_reference:
                        try:
                            pedido = Pedido.objects.get(id=external_reference)
                            if pedido.estado != 'pagado':
                                pedido.estado = 'pagado'
                                pedido.mercadopago_payment_id = payment.get('id')
                                pedido.save()
                        except Pedido.DoesNotExist:
                            print(f"Webhook: Pedido con ID {external_reference} no encontrado.")
            except Exception as e:
                print(f"Error procesando webhook de Mercado Pago: {e}")
        
        return Response(status=status.HTTP_200_OK)


class MercadoPagoPreferenceView(APIView):
    def post(self, request, *args, **kwargs):
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN_TEST)

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
            print("Mercado Pago API Response:", preference_response)

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
                print(f"ADVERTENCIA: No se encontró el pedido con ID {external_reference} para guardar el preference_id.")

            return Response({
                "preference_id": preference_id,
                "init_point": init_point
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error al crear preferencia de Mercado Pago: {e}")
            return Response({"error": "Hubo un problema al comunicarse con Mercado Pago."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
