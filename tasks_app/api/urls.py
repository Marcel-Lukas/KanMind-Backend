from django.urls import path
from .views import TaskListCreateView, CurrentUserTasksView, TaskDetailView, TaskCommentsView, TaskCommentDetailView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/', TaskCommentsView.as_view(), name='tasks-comments'),
    path('tasks/<int:task_id>/comments/<int:pk>/', TaskCommentDetailView.as_view(), name='task-comment-detail'),
    path('tasks/assigned-to-me/', CurrentUserTasksView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', CurrentUserTasksView().as_view(), name='tasks-reviewing'),
]
