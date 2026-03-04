"""Task and task-comment API views."""

from tasks_app.models import Task, TaskComment
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMemberOfBoard, IsBoardOwner, IsCommentAuthor
from .serializers import TaskSerializer, TaskCommentSerializer
from django.db import models
from rest_framework.exceptions import NotFound


class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks visible to the user or create a new task."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        """Restrict task list to boards the user can access."""
        user = self.request.user
        return Task.objects.filter(
            models.Q(board__members=user) | models.Q(board__owner=user)
        ).distinct()



class CurrentUserTasksView(generics.ListCreateAPIView):
    """Handle personalized task collections (assigned/reviewing)."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        """Select tasks by endpoint context for current user."""
        user = self.request.user
        if 'assigned-to-me' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user), 
                assignee=user,
            ).distinct()
        elif 'reviewing' in self.request.path:
            return Task.objects.filter(
                models.Q(board__members=user) | models.Q(board__owner=user),
                reviewer=user,
            ).distinct()
        else:
            return Task.objects.none()
        
    def perform_create(self, serializer):
        """Apply endpoint-specific default assignee/reviewer values."""
        if 'assigned-to-me' in self.request.path:
            serializer.save(assignee=self.request.user)
        elif 'reviewing' in self.request.path:
            serializer.save(reviewer=self.request.user)
        else:
            serializer.save()



class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single task."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        """Require board ownership for delete, membership otherwise."""
        if self.request.method == 'DELETE':
            return [IsBoardOwner()]
        return [IsAuthenticated(), IsMemberOfBoard()]

    def get_queryset(self):
        """Expose only tasks from boards user owns or joined."""
        user = self.request.user
        q_object = models.Q(board__members=user) | models.Q(board__owner=user)
        queryset = Task.objects.filter(q_object).distinct()
        return queryset
    
    def get_object(self):
        """Fetch task by primary key and enforce object permissions."""
        task_id = self.kwargs.get('pk')
        try:
            obj = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        self.check_object_permissions(self.request, obj)
        return obj
    


class TaskCommentsView(generics.ListCreateAPIView):
    """List and create comments for a specific task."""

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard] 

    def get_queryset(self):
        """Return comments bound to the URL task ID."""
        task_id = self.kwargs.get('pk')
        return TaskComment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """Persist new comment with current user as author."""
        task_id = self.kwargs.get('pk')
        serializer.save(
            author=self.request.user,
            task=Task.objects.get(pk=task_id)
        )



class TaskCommentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific comment of a task."""

    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """Scope comments to the task/comment IDs from the URL."""
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('pk')
        return TaskComment.objects.filter(
            task_id=task_id,
            pk=comment_id
        )
    
