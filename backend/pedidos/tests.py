from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Direccion, MetodoEnvio

class PedidoAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.client.force_authenticate(self.user)
        self.metodo = MetodoEnvio.objects.create(nombre='Estafeta', costo=299)

    def test_crear_pedido_guarda_direccion(self):
        url = reverse('pedido-list')
        data = {
            'direccion': {
                'nombre': 'John',
                'apellidos': 'Doe',
                'email': 'john@example.com',
                'calle': 'Calle 1',
                'numero_exterior': '123',
                'colonia': 'Centro',
                'ciudad': 'CDMX',
                'pais': 'MX',
                'estado': 'CDMX',
                'codigo_postal': '01010',
                'telefono': '5555555555'
            },
            'metodo_envio': self.metodo.id,
            'metodo_pago': 'transferencia',
            'indicaciones': '',
            'save_address': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Direccion.objects.filter(user=self.user).count(), 1)
