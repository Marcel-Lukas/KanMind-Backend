"""Task and task-comment API views."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tasks_app.models import Task, TaskComment

from .permissions import IsBoardOwner, IsCommentAuthor, IsMemberOfBoard
from .serializers import TaskCommentSerializer, TaskSerializer


def tasks_visible_to(user):
    """Return tasks belonging to boards the user owns or joined."""
    return Task.objects.filter(
        Q(board__members=user) | Q(board__owner=user)
    ).distinct()


class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks visible to the user or create a new task."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard]

    def get_queryset(self):
        """Restrict task list to boards the user can access."""
        return tasks_visible_to(self.request.user)


class _CurrentUserTaskListView(generics.ListCreateAPIView):
    """Base view for personalised task collections of the current user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    #: Name of the ``Task`` field used to filter/assign by the current user.
    user_field = ''

    def get_queryset(self):
        """Filter visible tasks by the configured role field."""
        if not self.user_field:
            return Task.objects.none()
        return tasks_visible_to(self.request.user).filter(
            **{self.user_field: self.request.user}
        )

    def perform_create(self, serializer):
        """Save task with the current user pre-filled for the role field."""
        if not self.user_field:
            serializer.save()
            return
        serializer.save(**{self.user_field: self.request.user})


class AssignedToMeTasksView(_CurrentUserTaskListView):
    """List or create tasks where the current user is the assignee."""

    user_field = 'assignee'


class ReviewingTasksView(_CurrentUserTaskListView):
    """List or create tasks where the current user is the reviewer."""

    user_field = 'reviewer'


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single task."""

    serializer_class = TaskSerializer

    def get_permissions(self):
        """Require board ownership for delete, membership otherwise."""
        if self.request.method == 'DELETE':
            return [IsBoardOwner()]
        return [IsAuthenticated(), IsMemberOfBoard()]

    def get_queryset(self):
        """Expose only tasks from boards the user owns or joined."""
        return tasks_visible_to(self.request.user)


class TaskCommentsView(generics.ListCreateAPIView):
    """List and create comments for a specific task."""

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoard]

    def get_queryset(self):
        """Return comments bound to the URL task ID."""
        return TaskComment.objects.filter(task_id=self.kwargs.get('pk'))

    def perform_create(self, serializer):
        """Persist new comment with the current user as author."""
        task = get_object_or_404(Task, pk=self.kwargs.get('pk'))
        serializer.save(author=self.request.user, task=task)


class TaskCommentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific comment of a task."""

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """Scope comments to the task/comment IDs from the URL."""
        return TaskComment.objects.filter(
            task_id=self.kwargs.get('task_id'),
            pk=self.kwargs.get('pk'),
        )
