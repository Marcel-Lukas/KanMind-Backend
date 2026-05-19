"""Tests for the aggregate counters exposed by the board list serializer."""

from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import Task


class BoardCounterTests(APITestCase):
    """Verify ``ticket_count``, ``tasks_to_do_count``, ``tasks_high_prio_count``."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.board = Board.objects.create(title='Counters', owner=cls.owner)
        Task.objects.create(
            board=cls.board, title='T1', description='', status='to-do',
            priority='high', due_date=date.today(),
        )
        Task.objects.create(
            board=cls.board, title='T2', description='', status='done',
            priority='low', due_date=date.today(),
        )

    def test_counters_reflect_related_tasks(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse('boards'))

        board_data = next(b for b in response.data if b['id'] == self.board.id)
        self.assertEqual(board_data['ticket_count'], 2)
        self.assertEqual(board_data['tasks_to_do_count'], 1)
        self.assertEqual(board_data['tasks_high_prio_count'], 1)
