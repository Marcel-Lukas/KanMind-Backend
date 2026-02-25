from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ]
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255) 
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewed_tasks', null=True, blank=True)
    due_date = models.DateField()
    comments_count = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.title


