"""Tests for the logout endpoint."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class LogoutViewTests(APITestCase):
    """Tests for the ``/api/logout/`` endpoint."""

    url = reverse('logout')

    def setUp(self):
        self.user = User.objects.create_user(
            username='Logout User',
            email='logout@example.com',
            password='StrongPass123!',
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_deletes_token_for_authenticated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
