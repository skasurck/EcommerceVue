from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Producto, PrecioEscalonado


class PrecioEscalonadoAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="pass1234")
        self.user.perfil.rol = "admin"
        self.user.perfil.save()
        self.client.force_authenticate(self.user)

        self.producto = Producto.objects.create(
            nombre="Prod",
            precio_normal=100,
            stock=10,
        )
        self.tier = PrecioEscalonado.objects.create(
            producto=self.producto, cantidad_minima=5, precio_unitario=90
        )

    def test_actualizar_precios_escalonados(self):
        url = reverse("producto-detail", args=[self.producto.id])
        payload = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": True,
            "estado_inventario": "en_existencia",
            "visibilidad": True,
            "estado": "borrador",
            "precios_escalonados": [
                {"id": self.tier.id, "cantidad_minima": 5, "precio_unitario": "95"},
                {"cantidad_minima": 20, "precio_unitario": "80"},
            ],
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        tiers = list(
            PrecioEscalonado.objects.filter(producto=self.producto)
            .order_by("cantidad_minima")
            .values_list("cantidad_minima", "precio_unitario")
        )
        self.assertEqual(tiers, [(5, Decimal("95")), (20, Decimal("80"))])

    def test_actualizar_precios_escalonados_multipart(self):
        url = reverse("producto-detail", args=[self.producto.id])
        data = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": "true",
            "estado_inventario": "en_existencia",
            "visibilidad": "true",
            "estado": "borrador",
            "precios_escalonados[0][id]": str(self.tier.id),
            "precios_escalonados[0][cantidad_minima]": "5",
            "precios_escalonados[0][precio_unitario]": "95",
            "precios_escalonados[1][cantidad_minima]": "20",
            "precios_escalonados[1][precio_unitario]": "80",
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        tiers = list(
            PrecioEscalonado.objects.filter(producto=self.producto)
            .order_by("cantidad_minima")
            .values_list("cantidad_minima", "precio_unitario")
        )
        self.assertEqual(tiers, [(5, Decimal("95")), (20, Decimal("80"))])

    def test_update_con_valores_null(self):
        """Acepta cadenas 'null' o vacías en campos opcionales."""
        url = reverse("producto-detail", args=[self.producto.id])
        data = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": "true",
            "estado_inventario": "en_existencia",
            "visibilidad": "true",
            "estado": "borrador",
            "categoria": "null",
            "marca": "",
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertIsNone(self.producto.categoria)
        self.assertIsNone(self.producto.marca)
