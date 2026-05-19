"""Tests for listing and creating comments on a task."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import TaskComment

from .helpers import make_task


class TaskCommentsViewTests(APITestCase):
    """Tests for the ``/api/tasks/<pk>/comments/`` endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.outsider = User.objects.create_user(username='outsider', password='pw12345!')

        cls.board = Board.objects.create(title='Board', owner=cls.owner)
        cls.board.members.add(cls.member)
        cls.task = make_task(cls.board)
        cls.url = reverse('tasks-comments', kwargs={'pk': cls.task.pk})

    def test_outsider_cannot_access_comments(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_create_comment_with_self_as_author(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            self.url, {'content': 'Looks good!'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = TaskComment.objects.get(task=self.task)
        self.assertEqual(comment.author, self.member)
        self.assertEqual(comment.content, 'Looks good!')

    def test_list_returns_comments_for_task(self):
        TaskComment.objects.create(task=self.task, author=self.owner, content='A')
        TaskComment.objects.create(task=self.task, author=self.member, content='B')

        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
