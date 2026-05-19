"""Unit tests for the ``Board`` model."""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from board_app.models import Board


class BoardModelTests(APITestCase):
    """Unit tests for the ``Board`` model."""

    def test_str_returns_title(self):
        owner = User.objects.create_user(username='owner', password='pw12345!')
        board = Board.objects.create(title='My Board', owner=owner)
        self.assertEqual(str(board), 'My Board')
