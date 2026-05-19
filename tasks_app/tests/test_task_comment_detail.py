"""Tests for retrieving and deleting a single comment."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import TaskComment

from .helpers import make_task


class TaskCommentDetailViewTests(APITestCase):
    """Tests for the ``/api/tasks/<task_id>/comments/<pk>/`` endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author', password='pw12345!')
        cls.other_member = User.objects.create_user(username='other', password='pw12345!')

        cls.board = Board.objects.create(title='Board', owner=cls.author)
        cls.board.members.add(cls.other_member)
        cls.task = make_task(cls.board)
        cls.comment = TaskComment.objects.create(
            task=cls.task, author=cls.author, content='Mine',
        )
        cls.url = reverse(
            'task-comment-detail',
            kwargs={'task_id': cls.task.pk, 'pk': cls.comment.pk},
        )

    def test_author_can_delete_own_comment(self):
        self.client.force_authenticate(self.author)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskComment.objects.filter(pk=self.comment.pk).exists())

    def test_other_member_cannot_delete_foreign_comment(self):
        self.client.force_authenticate(self.other_member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
