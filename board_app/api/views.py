"""Board API views for CRUD and user email lookup."""

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from board_app.models import Board

from .permissions import BoardAccessPermission
from .serializers import (
    BoardSerializer,
    BoardUpdateSerializer,
    SingleBoardSerializer,
)


class BoardListView(generics.ListCreateAPIView):
    """List boards for current user or create a new board."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return boards where the user is owner or member."""
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        """Always set the current user as board owner."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single board by permissions."""

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, BoardAccessPermission]

    serializer_classes = {
        'GET': SingleBoardSerializer,
        'PATCH': BoardUpdateSerializer,
    }

    def get_serializer_class(self):
        """Use detail serializer for reads and update serializer for PATCH."""
        return self.serializer_classes.get(self.request.method, SingleBoardSerializer)


class EmailCheckView(APIView):
    """Resolve a user by email for board member assignment."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return compact user payload for a given email query param."""
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'detail': 'Email is required as a query parameter'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        fullname = f'{user.first_name}{user.last_name}'.strip() or user.username
        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': fullname,
        })
