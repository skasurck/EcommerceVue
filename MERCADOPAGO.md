# Prueba de Checkout Pro (Mercado Pago)

Guía rápida para integrar Checkout Pro usando credenciales de prueba.

## 1. Variables de entorno

Backend:

```bash
MP_ACCESS_TOKEN_TEST=tu_access_token_de_prueba
```

Frontend (si usarás SDK o redirección directa):

```bash
VITE_MP_PUBLIC_KEY_TEST=tu_public_key_de_prueba
```

Mantén separados los valores de prueba y los de producción.

## 2. Endpoint para crear la *preference*

1. Instala el SDK oficial:
   ```bash
   pip install mercadopago
   ```
2. Crea un endpoint `POST /pagos/mercadopago/preferencias/` que reciba los ítems del pedido en curso.
3. Dentro del endpoint usa `mercadopago.SDK(MP_ACCESS_TOKEN_TEST)` y ejecuta `sdk.preference().create(...)`.
4. Devuelve al frontend el `init_point` (checkout web) y el `preference_id`.

## 3. Integración en el paso 3 del checkout

- Cuando el usuario elija “Mercado Pago”, llama al endpoint anterior antes de crear el pedido local.
- Redirige al `init_point` recibido (por ejemplo `window.location.href = init_point` o abre en nueva pestaña).
- Define `back_urls` en la *preference* (`success`, `pending`, `failure`) y apunta `success` a `/gracias`.

## 4. Sincronizar el pedido

- Al regresar a `/gracias`, lee los parámetros `status`, `preference_id` y `payment_id`.
- Registra un webhook (`/webhooks/mercadopago/`). Cuando Mercado Pago envíe un `topic=merchant_order` o `topic=payment`, consulta el detalle con el SDK y marca el pedido como “pagado” si `status === "approved"`.

## 5. Flujo sugerido

1. Checkout Step3 → crea el pedido local en estado **pendiente**.
2. Llama al endpoint de Mercado Pago → redirige al `init_point`.
3. El cliente paga → Mercado Pago redirige a `/gracias?status=approved&payment_id=...`.
4. El webhook confirma y marca el pedido como **pagado**.
5. La página de gracias lee `payment_id` y muestra el estado final (aprobado, pendiente o rechazado).

Con esto podrás probar pagos sin tocar datos reales hasta que cambies a credenciales de producción.
