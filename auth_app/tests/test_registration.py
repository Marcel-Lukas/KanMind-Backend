"""Tests for the user registration endpoint."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RegistrationViewTests(APITestCase):
    """Tests for the ``/api/registration/`` endpoint."""

    url = reverse('registration')

    @classmethod
    def setUpTestData(cls):
        """Create a pre-existing user to test email collision."""
        cls.existing_user = User.objects.create_user(
            username='Existing User',
            email='existing@example.com',
            password='ExistingPass123!',
        )

    def _valid_payload(self, **overrides):
        """Return a baseline registration payload with optional overrides."""
        payload = {
            'fullname': 'Jane Doe',
            'email': 'jane@example.com',
            'password': 'StrongPass123!',
            'repeated_password': 'StrongPass123!',
        }
        payload.update(overrides)
        return payload

    def test_registration_creates_user_and_returns_token(self):
        response = self.client.post(self.url, self._valid_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], 'jane@example.com')
        self.assertEqual(response.data['fullname'], 'Jane Doe')

        user = User.objects.get(email='jane@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_registration_with_single_name_keeps_last_name_empty(self):
        response = self.client.post(
            self.url,
            self._valid_payload(fullname='Madonna'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='jane@example.com')
        self.assertEqual(user.first_name, 'Madonna')
        self.assertEqual(user.last_name, '')

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            self.url,
            self._valid_payload(repeated_password='Different123!'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('repeated_password', response.data)

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            self.url,
            self._valid_payload(email='existing@example.com'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            self.url,
            self._valid_payload(password='123', repeated_password='123'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_requires_all_fields(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
