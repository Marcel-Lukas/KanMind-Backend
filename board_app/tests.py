from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from board_app.models import Board


class BoardPatchEndpointTests(APITestCase):
    """Regression tests for board PATCH endpoint behavior."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner_user",
            email="owner@example.com",
            password="pass1234",
        )
        self.member = User.objects.create_user(
            username="member_user",
            email="member@example.com",
            password="pass1234",
        )
        self.other_member = User.objects.create_user(
            username="other_member_user",
            email="other_member@example.com",
            password="pass1234",
        )
        self.outsider = User.objects.create_user(
            username="outsider_user",
            email="outsider@example.com",
            password="pass1234",
        )

        self.owner_token = Token.objects.create(user=self.owner)
        self.member_token = Token.objects.create(user=self.member)
        self.outsider_token = Token.objects.create(user=self.outsider)

        self.board = Board.objects.create(title="Initial Board", owner=self.owner)
        self.board.members.set([self.owner, self.member])

    def _board_url(self):
        return f"/api/boards/{self.board.id}/"

    def test_owner_can_patch_title_and_members(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._board_url(),
            {"title": "Changed title", "members": [self.owner.id, self.other_member.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, "Changed title")
        self.assertSetEqual(
            set(self.board.members.values_list("id", flat=True)),
            {self.owner.id, self.other_member.id},
        )

    def test_member_can_patch_board(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.member_token.key}")

        response = self.client.patch(
            self._board_url(),
            {"title": "Changed by member", "members": [self.owner.id, self.member.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_outsider_gets_403_on_patch(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.outsider_token.key}")

        response = self.client.patch(
            self._board_url(),
            {"title": "Forbidden", "members": [self.owner.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_patch_invalid_member_id_returns_400(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._board_url(),
            {"title": "Bad members", "members": [999999]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("members", response.data)

    def test_patch_rejects_tasks_field(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.owner_token.key}")

        response = self.client.patch(
            self._board_url(),
            {"title": "Try task update", "members": [self.owner.id], "tasks": []},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("tasks", response.data)
