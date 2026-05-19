"""URL patterns for task and comment endpoints."""

from django.urls import path

from .views import (
    AssignedToMeTasksView,
    ReviewingTasksView,
    TaskCommentDetailView,
    TaskCommentsView,
    TaskDetailView,
    TaskListCreateView,
)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/assigned-to-me/', AssignedToMeTasksView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='tasks-reviewing'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/', TaskCommentsView.as_view(), name='tasks-comments'),
    path(
        'tasks/<int:task_id>/comments/<int:pk>/',
        TaskCommentDetailView.as_view(),
        name='task-comment-detail',
    ),
]
