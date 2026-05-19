"""Tests for ``assigned-to-me`` and ``reviewing`` filtered task lists."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board

from .helpers import make_task


class CurrentUserTasksViewTests(APITestCase):
    """Tests for the per-user task filter endpoints."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.board = Board.objects.create(title='Board', owner=cls.owner)
        cls.board.members.add(cls.member)

        cls.assigned = make_task(cls.board, title='Assigned', assignee=cls.member)
        cls.reviewing = make_task(cls.board, title='Reviewing', reviewer=cls.member)
        cls.unrelated = make_task(cls.board, title='Unrelated')

    def test_assigned_to_me_returns_only_assigned_tasks(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse('tasks-assigned'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {task['title'] for task in response.data}
        self.assertEqual(titles, {'Assigned'})

    def test_reviewing_returns_only_reviewer_tasks(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse('tasks-reviewing'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {task['title'] for task in response.data}
        self.assertEqual(titles, {'Reviewing'})
