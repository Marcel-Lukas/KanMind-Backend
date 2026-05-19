"""Tests for the ``/api/tasks/`` list and create endpoint."""

from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import Task

from .helpers import make_task


class TaskListCreateViewTests(APITestCase):
    """Tests for listing and creating tasks."""

    url = reverse('tasks')

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.outsider = User.objects.create_user(username='outsider', password='pw12345!')

        cls.board = Board.objects.create(title='Board', owner=cls.owner)
        cls.board.members.add(cls.member)

        cls.other_board = Board.objects.create(title='Other', owner=cls.outsider)

        cls.visible_task = make_task(cls.board, title='Visible')
        cls.hidden_task = make_task(cls.other_board, title='Hidden')

    def _task_payload(self, **overrides):
        """Return a baseline task payload with optional overrides."""
        payload = {
            'board': self.board.id,
            'title': 'New',
            'description': 'desc',
            'status': 'to-do',
            'priority': 'low',
            'due_date': str(date.today()),
        }
        payload.update(overrides)
        return payload

    def test_unauthenticated_user_cannot_list_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_only_tasks_from_accessible_boards(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {task['title'] for task in response.data}
        self.assertEqual(titles, {'Visible'})

    def test_member_can_create_task(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            self.url,
            self._task_payload(assignee_id=self.member.id),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title='New').exists())

    def test_non_member_cannot_create_task_on_foreign_board(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            self.url, self._task_payload(title='Sneaky'), format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignee_must_belong_to_board(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            self.url,
            self._task_payload(
                title='Invalid Assignee',
                assignee_id=self.outsider.id,
            ),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
