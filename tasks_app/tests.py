from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import Task


class TaskCreateEndpointTests(APITestCase):
    """Regression tests for task creation validations."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="task_owner",
            email="task_owner@example.com",
            password="pass1234",
        )
        self.member = User.objects.create_user(
            username="task_member",
            email="task_member@example.com",
            password="pass1234",
        )
        self.outsider = User.objects.create_user(
            username="task_outsider",
            email="task_outsider@example.com",
            password="pass1234",
        )
        self.owner_token = Token.objects.create(user=self.owner)
        self.member_token = Token.objects.create(user=self.member)
        self.outsider_token = Token.objects.create(user=self.outsider)

        self.board = Board.objects.create(title="Task Test Board", owner=self.owner)
        self.board.members.set([self.member])

    def _tasks_url(self):
        return "/api/tasks/"

    def test_create_task_allows_board_owner_as_assignee(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "board": self.board.id,
                "title": "Owner assigned task",
                "description": "desc",
                "status": "to-do",
                "priority": "high",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["assignee"]["id"], self.owner.id)
        self.assertEqual(response.data["reviewer"]["id"], self.member.id)

    def test_create_task_rejects_assignee_outside_board(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "board": self.board.id,
                "title": "Invalid assignee",
                "description": "desc",
                "status": "to-do",
                "priority": "high",
                "assignee_id": self.outsider.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_create_task_requires_board(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "title": "No board",
                "description": "desc",
                "status": "to-do",
                "priority": "high",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("board", response.data)

    def test_create_task_with_unknown_board_returns_404(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "board": 999999,
                "title": "Missing board",
                "description": "desc",
                "status": "review",
                "priority": "medium",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_task_list_returns_200_for_board_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.member_token.key}")

        response = self.client.get(self._tasks_url())

        self.assertEqual(response.status_code, 200)

    def test_create_task_rejects_invalid_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "board": self.board.id,
                "title": "Invalid status",
                "description": "desc",
                "status": "in_progress",
                "priority": "medium",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_create_task_rejects_invalid_priority(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.post(
            self._tasks_url(),
            {
                "board": self.board.id,
                "title": "Invalid priority",
                "description": "desc",
                "status": "review",
                "priority": "urgent",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
                "due_date": "2026-03-20",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("priority", response.data)


class TaskPatchEndpointTests(APITestCase):
    """Regression tests for task PATCH validation and permissions."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="patch_task_owner",
            email="patch_task_owner@example.com",
            password="pass1234",
        )
        self.member = User.objects.create_user(
            username="patch_task_member",
            email="patch_task_member@example.com",
            password="pass1234",
        )
        self.outsider = User.objects.create_user(
            username="patch_task_outsider",
            email="patch_task_outsider@example.com",
            password="pass1234",
        )

        self.owner_token = Token.objects.create(user=self.owner)
        self.member_token = Token.objects.create(user=self.member)
        self.outsider_token = Token.objects.create(user=self.outsider)

        self.board = Board.objects.create(title="Patch Task Board", owner=self.owner)
        self.board.members.set([self.member])

        self.task = Task.objects.create(
            board=self.board,
            title="Initial task",
            description="initial",
            status="to-do",
            priority="medium",
            assignee=self.member,
            reviewer=self.owner,
            due_date="2026-03-20",
        )

    def _task_url(self, task_id=None):
        target_task_id = task_id or self.task.id
        return f"/api/tasks/{target_task_id}/"

    def test_owner_can_patch_allowed_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(),
            {
                "title": "Updated title",
                "status": "done",
                "priority": "high",
                "assignee_id": self.owner.id,
                "reviewer_id": self.member.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated title")
        self.assertEqual(self.task.status, "done")
        self.assertEqual(self.task.priority, "high")
        self.assertEqual(self.task.assignee_id, self.owner.id)
        self.assertEqual(self.task.reviewer_id, self.member.id)

    def test_member_can_patch_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.member_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"description": "updated by member"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_outsider_gets_403_on_patch(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.outsider_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"title": "forbidden"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_patch_without_auth_returns_401(self):
        response = self.client.patch(
            self._task_url(),
            {"title": "unauthorized"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_patch_unknown_task_returns_404(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(task_id=999999),
            {"title": "not found"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_patch_rejects_board_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"board": self.board.id, "title": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("board", response.data)

    def test_patch_rejects_unknown_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"comments_count": 42},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("comments_count", response.data)

    def test_patch_rejects_invalid_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"status": "in_progress"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_patch_rejects_invalid_priority(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._task_url(),
            {"priority": "urgent"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("priority", response.data)
