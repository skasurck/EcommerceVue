from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Perfil


class PerfilAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester2", password="pass1234")
        self.client.force_authenticate(self.user)
        # Eliminar perfil para simular usuarios existentes sin perfil
        self.user.perfil.delete()

    def test_crear_perfil_en_update(self):
        url = reverse("profile")
        data = {
            "first_name": "Juan",
            "perfil": {"telefono": "5551234", "empresa": "ACME"},
        }
        resp = self.client.put(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        perfil = Perfil.objects.get(user=self.user)
        self.assertEqual(perfil.telefono, "5551234")
        self.assertEqual(perfil.empresa, "ACME")
