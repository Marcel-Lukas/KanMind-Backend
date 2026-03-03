from django.urls import path
from .views import TaskListCreateView, CurrentUserTasksView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/assigned-to-me/', CurrentUserTasksView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', CurrentUserTasksView().as_view(), name='tasks-reviewing'),
]
