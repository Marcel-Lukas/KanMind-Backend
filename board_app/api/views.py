from board_app.models import Board
from .serializers import BoardSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics


class BoardView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



