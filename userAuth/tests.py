from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from userAuth.models import UserCeprunsa


class GoogleAuthViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("google-auth")
        self.valid_token = "valid_token"
        self.google_user_info = {
            "email": "testuser@example.com",
        }

    @patch("requests.get")
    def test_google_auth_successful(self, mock_get):
        # Simula la respuesta de la API de Google
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_user_info

        # Crea un usuario de prueba
        user = UserCeprunsa.objects.createUserWithGoogle(
            email=self.google_user_info["email"]
        )

        # Envía una solicitud con el token válido
        response = self.client.post(
            self.url, {"token": self.valid_token}, format="json"
        )

        # Verifica que el usuario haya recibido un token de acceso
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    @patch("requests.get")
    def test_google_auth_user_not_registered(self, mock_get):
        # Simula la respuesta de la API de Google
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_user_info

        # Envía una solicitud con el token válido
        response = self.client.post(
            self.url, {"token": self.valid_token}, format="json"
        )

        # Verifica que el usuario no registrado reciba un 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "User no está registrado")

    @patch("requests.get")
    def test_google_auth_invalid_token(self, mock_get):
        # Simula un token inválido
        mock_get.return_value.status_code = 400

        # Envía una solicitud con el token inválido
        response = self.client.post(self.url, {"token": "invalid_token"}, format="json")

        # Verifica que la respuesta sea de error 400 para un token inválido
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Token inválido")
