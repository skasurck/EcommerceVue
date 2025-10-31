from decimal import Decimal
from django.urls import reverse
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from carrito.models import Cart
from productos.models import Producto

from pedidos.models import Direccion, MetodoEnvio, Pedido

class PedidoAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass1234')
        self.client.force_authenticate(self.user)
        self.metodo = MetodoEnvio.objects.create(nombre='Estafeta', costo=299)
        self.producto = Producto.objects.create(nombre='Prod', precio_normal=100, stock=5)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.items.create(producto=self.producto, cantidad=2)
        self.producto.stock -= 2
        self.producto.save()

    def _crear_pedido_simple(self, user, email='john@example.com', subtotal='100', envio='20'):
        direccion = Direccion.objects.create(
            user=user,
            nombre='John',
            apellidos='Doe',
            email=email,
            calle='Calle 1',
            numero_exterior='123',
            colonia='Centro',
            ciudad='CDMX',
            pais='MX',
            estado='CDMX',
            codigo_postal='01010',
            telefono='5555555555',
        )
        return Pedido.objects.create(
            user=user,
            direccion=direccion,
            metodo_envio=self.metodo,
            metodo_pago='transferencia',
            subtotal=Decimal(subtotal),
            costo_envio=Decimal(envio),
            total=Decimal(subtotal) + Decimal(envio),
        )

    def test_crear_pedido_guarda_items_y_totales(self):
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
        pedido = Pedido.objects.get(id=response.data['id'])
        self.assertEqual(pedido.subtotal, Decimal('200'))
        self.assertEqual(pedido.total, Decimal('499'))
        self.assertEqual(pedido.items.count(), 1)
        item = pedido.items.first()
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.precio_unitario, Decimal('100'))
        self.assertEqual(item.subtotal, Decimal('200'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertEqual(self.cart.items.count(), 0)

    def test_cancelar_pedido_devuelve_stock(self):
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
        pedido = Pedido.objects.get(id=response.data['id'])
        pedido.estado = 'pagado'
        pedido.save()

        pedido.estado = 'cancelado'
        pedido.save()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)

        pedido.estado = 'cancelado'
        pedido.save()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
        pedido.refresh_from_db()
        self.assertEqual(pedido.historial.filter(descripcion__icontains='Stock devuelto').count(), 1)

    def test_listado_solo_incluye_pedidos_del_usuario(self):
        propio = self._crear_pedido_simple(self.user, email='tester@example.com')
        User = get_user_model()
        otro = User.objects.create_user(username='other', password='pass1234')
        self._crear_pedido_simple(otro, email='other@example.com')

        response = self.client.get(reverse('pedido-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resultados = response.data['results'] if 'results' in response.data else response.data
        ids = {item['id'] for item in resultados}
        self.assertEqual(ids, {propio.id})

    def test_admin_puede_ver_todos_los_pedidos(self):
        propio = self._crear_pedido_simple(self.user, email='tester@example.com')
        User = get_user_model()
        otro = User.objects.create_user(username='other-admin', password='pass1234')
        ajeno = self._crear_pedido_simple(otro, email='other-admin@example.com')

        admin = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        admin.is_superuser = True
        admin.save(update_fields=['is_superuser'])
        admin.perfil.rol = 'admin'
        admin.perfil.save(update_fields=['rol'])

        self.client.force_authenticate(admin)
        response = self.client.get(reverse('pedido-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resultados = response.data['results'] if 'results' in response.data else response.data
        ids = {item['id'] for item in resultados}
        self.assertEqual(ids, {propio.id, ajeno.id})


class DireccionUserPopulateTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='john', password='pass1234')
        self.client.force_authenticate(self.user)

    def test_crear_direccion_autocompleta_usuario(self):
        url = reverse('direccion-list')
        data = {
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan@example.com',
            'calle': 'Calle 1',
            'numero_exterior': '1',
            'colonia': 'Centro',
            'ciudad': 'CDMX',
            'pais': 'MX',
            'estado': 'CDMX',
            'codigo_postal': '01010',
            'telefono': '5555555555',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Juan')
        self.assertEqual(self.user.last_name, 'Pérez')
        self.assertEqual(self.user.email, 'juan@example.com')
        self.assertEqual(self.user.perfil.telefono, '5555555555')


class DireccionDefaultTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='john2', password='pass1234')
        self.client.force_authenticate(self.user)

    def _crear_direccion(self, **kwargs):
        data = {
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan@example.com',
            'calle': 'Calle 1',
            'numero_exterior': '1',
            'colonia': 'Centro',
            'ciudad': 'CDMX',
            'pais': 'MX',
            'estado': 'CDMX',
            'codigo_postal': '01010',
            'telefono': '5555555555',
        }
        data.update(kwargs)
        return self.client.post(reverse('direccion-list'), data, format='json')

    def test_predeterminada_al_eliminar(self):
        r1 = self._crear_direccion()
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        d1 = Direccion.objects.get(id=r1.data['id'])
        self.assertTrue(d1.predeterminada)
        r2 = self._crear_direccion(calle='Calle 2', numero_exterior='2')
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)
        d2 = Direccion.objects.get(id=r2.data['id'])
        self.assertTrue(d1.predeterminada)
        del_url = reverse('direccion-detail', args=[d1.id])
        self.client.delete(del_url)
        d2.refresh_from_db()
        self.assertTrue(d2.predeterminada)


class DireccionListFlagTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='john3', password='pass1234')
        self.client.force_authenticate(self.user)

    def test_lista_incluye_tiene_direccion(self):
        url = reverse('direccion-list')
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertFalse(r.data['tiene_direccion'])
        self.assertEqual(r.data['direcciones'], [])
        data = {
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan@example.com',
            'calle': 'Calle 1',
            'numero_exterior': '1',
            'colonia': 'Centro',
            'ciudad': 'CDMX',
            'pais': 'MX',
            'estado': 'CDMX',
            'codigo_postal': '01010',
            'telefono': '5555555555',
        }
        self.client.post(url, data, format='json')
        r = self.client.get(url)
        self.assertTrue(r.data['tiene_direccion'])
        self.assertEqual(len(r.data['direcciones']), 1)
