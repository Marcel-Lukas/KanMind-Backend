from django.urls import path
from .views import TaskListCreateView, CurrentUserTasksView, TaskDetailView, TaskCommentsView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/', TaskCommentsView.as_view(), name='tasks-comments'),
    path('tasks/assigned-to-me/', CurrentUserTasksView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', CurrentUserTasksView().as_view(), name='tasks-reviewing'),
]
