"""Shared helpers for task-related tests."""

from datetime import date

from tasks_app.models import Task


def make_task(board, **overrides):
    """Create a ``Task`` instance with sensible default values."""
    defaults = {
        'title': 'Sample Task',
        'description': 'A description',
        'status': 'to-do',
        'priority': 'medium',
        'due_date': date.today(),
    }
    defaults.update(overrides)
    return Task.objects.create(board=board, **defaults)
