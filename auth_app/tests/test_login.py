"""Tests for the login endpoint."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginViewTests(APITestCase):
    """Tests for the ``/api/login/`` endpoint."""

    url = reverse('login')

    @classmethod
    def setUpTestData(cls):
        cls.password = 'StrongPass123!'
        cls.user = User.objects.create_user(
            username='John Smith',
            email='john@example.com',
            password=cls.password,
            first_name='John',
            last_name='Smith',
        )

    def test_login_with_valid_credentials_returns_token(self):
        response = self.client.post(
            self.url,
            {'email': self.user.email, 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)

    def test_login_is_case_insensitive_for_email(self):
        response = self.client.post(
            self.url,
            {'email': self.user.email.upper(), 'password': self.password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            self.url,
            {'email': self.user.email, 'password': 'WrongPassword!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_unknown_email(self):
        response = self.client.post(
            self.url,
            {'email': 'nobody@example.com', 'password': self.password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
