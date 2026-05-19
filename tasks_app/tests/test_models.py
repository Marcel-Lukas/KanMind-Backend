"""Unit tests for the task and comment models."""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import TaskComment

from .helpers import make_task


class TaskModelTests(APITestCase):
    """Unit tests for the ``Task`` and ``TaskComment`` models."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='owner', password='pw12345!')
        cls.board = Board.objects.create(title='B', owner=cls.user)

    def test_task_str_returns_title(self):
        task = make_task(self.board, title='Hello')
        self.assertEqual(str(task), 'Hello')

    def test_comment_str_contains_author_and_excerpt(self):
        task = make_task(self.board)
        comment = TaskComment.objects.create(
            task=task, author=self.user, content='Hello world',
        )
        self.assertIn(self.user.username, str(comment))
        self.assertIn('Hello', str(comment))
