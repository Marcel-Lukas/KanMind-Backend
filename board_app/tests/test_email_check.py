"""Tests for the email lookup endpoint."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EmailCheckViewTests(APITestCase):
    """Tests for the ``/api/email-check/`` endpoint."""

    url = reverse('email-check')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='Sample User',
            email='sample@example.com',
            password='pw12345!',
            first_name='Sample',
            last_name='User',
        )

    def test_lookup_requires_authentication(self):
        response = self.client.get(self.url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lookup_returns_user_payload(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {'email': self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('fullname', response.data)

    def test_missing_email_param_returns_400(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_email_returns_404(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {'email': 'nobody@example.com'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
