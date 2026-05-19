"""Tests for retrieve/update/delete on a single board."""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from board_app.models import Board


class BoardDetailViewTests(APITestCase):
    """Tests for the ``/api/boards/<pk>/`` endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='pw12345!')
        cls.member = User.objects.create_user(username='member', password='pw12345!')
        cls.outsider = User.objects.create_user(username='outsider', password='pw12345!')

        cls.board = Board.objects.create(title='Board', owner=cls.owner)
        cls.board.members.add(cls.member)
        cls.detail_url = reverse('board-detail', kwargs={'pk': cls.board.pk})

    def test_outsider_receives_403(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_retrieve_board(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.board.pk)
        self.assertEqual(response.data['owner_id'], self.owner.id)

    def test_member_can_patch_title(self):
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            self.detail_url, {'title': 'Renamed'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, 'Renamed')

    def test_patch_rejects_unknown_fields(self):
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            self.detail_url, {'owner': self.member.id}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_rejects_duplicate_members(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.detail_url,
            {'members': [self.member.id, self.member.id]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_delete(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(pk=self.board.pk).exists())
