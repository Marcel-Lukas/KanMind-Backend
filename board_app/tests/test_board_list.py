"""Tests for listing and creating boards."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board


class BoardListViewTests(APITestCase):
    """Tests for the ``/api/boards/`` list and create endpoint."""

    url = reverse('boards')

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.outsider = User.objects.create_user(username='outsider', password='pw12345!')

        cls.owned_board = Board.objects.create(title='Owned', owner=cls.owner)
        cls.member_board = Board.objects.create(title='Joined', owner=cls.outsider)
        cls.member_board.members.add(cls.member)
        cls.owned_board.members.add(cls.member)

    def test_unauthenticated_user_cannot_list_boards(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_only_their_boards(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {board['title'] for board in response.data}
        self.assertEqual(titles, {'Owned'})

    def test_member_sees_owned_and_joined_boards(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {board['title'] for board in response.data}
        self.assertEqual(titles, {'Owned', 'Joined'})

    def test_create_board_assigns_current_user_as_owner(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            self.url,
            {'title': 'New Board', 'members': [self.member.id]},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.get(title='New Board')
        self.assertEqual(board.owner, self.outsider)
        self.assertIn(self.member, board.members.all())
