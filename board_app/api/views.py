from board_app.models import Board
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer
from .permissions import BoardAccessPermission


class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class BoardDetailView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, BoardAccessPermission]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SingleBoardSerializer 
        elif self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return SingleBoardSerializer
    


