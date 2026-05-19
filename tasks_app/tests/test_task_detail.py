"""Tests for the ``/api/tasks/<pk>/`` endpoint."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board

from .helpers import make_task


class TaskDetailViewTests(APITestCase):
    """Tests for retrieve/update/delete on a single task."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.outsider = User.objects.create_user(username='outsider', password='pw12345!')

        cls.board = Board.objects.create(title='Board', owner=cls.owner)
        cls.board.members.add(cls.member)
        cls.other_board = Board.objects.create(title='Other', owner=cls.owner)

        cls.task = make_task(cls.board, title='Detail')
        cls.url = reverse('task-detail', kwargs={'pk': cls.task.pk})

    def test_outsider_receives_403(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_retrieve_task(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task.pk)

    def test_member_can_patch_allowed_fields(self):
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            self.url, {'title': 'Updated'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated')

    def test_patch_rejects_unknown_fields(self):
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            self.url, {'comments_count': 99}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_changing_board_is_forbidden(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.url, {'board': self.other_board.id}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_board_owner_can_delete(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_missing_task_returns_404(self):
        self.client.force_authenticate(self.owner)
        url = reverse('task-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
