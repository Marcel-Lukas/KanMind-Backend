from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    """Kanban board with one owner and multiple members."""

    title = models.CharField(max_length=40)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        """Return human-readable board title."""
        return self.title
    
