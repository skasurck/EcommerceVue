from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class RegistroRateThrottle(AnonRateThrottle):
    scope = 'registro'


class PedidoCreateRateThrottle(AnonRateThrottle):
    scope = 'pedido_create'
