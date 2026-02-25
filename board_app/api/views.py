from board_app.models import Board
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer
from .permissions import BoardAccessPermission
from django.contrib.auth.models import User


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
    


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'Email is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            fullname = f"{user.first_name}{user.last_name}".strip() or user.username
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': fullname
            })
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


