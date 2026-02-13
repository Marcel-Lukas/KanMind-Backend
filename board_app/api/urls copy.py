from django.urls import path
from .views import BoardView

urlpatterns = [
    path('boards/', BoardView.as_view(), name='boards'),
]