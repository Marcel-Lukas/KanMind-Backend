from tasks_app.models import Task
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMemberOfBoard
from .serializers import TaskSerializer
from django.db import models


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(board__members=user) | models.Q(board__owner=user)
        ).distinct()

