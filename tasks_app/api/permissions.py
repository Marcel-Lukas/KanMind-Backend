"""Custom permission classes for task and comment access."""

from django.shortcuts import get_object_or_404
from rest_framework import permissions

from board_app.models import Board
from tasks_app.models import Task


def _is_board_member_or_owner(user, board):
    """Return ``True`` if the user owns or is assigned to the board."""
    if board is None or not user.is_authenticated:
        return False
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


class IsMemberOfBoard(permissions.BasePermission):
    """Allow access only to board members or owners."""

    BOARD_FIELD_KEYS = ('board', 'board_id', 'boardId')

    def has_permission(self, request, view):
        """Validate board access for non-object requests."""
        board = self._resolve_board_from_request(request, view)
        if board is None:
            return self._allow_without_board_context(request)
        return _is_board_member_or_owner(request.user, board)

    def has_object_permission(self, request, view, obj):
        """Validate board access for object-level requests."""
        board = self._extract_board_from_object(obj)
        return _is_board_member_or_owner(request.user, board)

    def _resolve_board_from_request(self, request, view):
        """Resolve the board from request data or URL kwargs."""
        board_id = self._get_board_id_from_data(request)
        if board_id is not None:
            return get_object_or_404(Board, pk=board_id)

        task_id = view.kwargs.get('pk') or view.kwargs.get('task_id')
        if task_id:
            return get_object_or_404(Task, pk=task_id).board
        return None

    def _get_board_id_from_data(self, request):
        """Support common board field names in incoming payloads."""
        data = getattr(request, 'data', {}) or {}
        for key in self.BOARD_FIELD_KEYS:
            if key in data:
                return data.get(key)
        return None

    def _allow_without_board_context(self, request):
        """Handle list/create calls where the board context is resolved later."""
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        if request.method == 'POST':
            return True
        return False

    def _extract_board_from_object(self, obj):
        """Extract the board relation from task or comment objects."""
        if hasattr(obj, 'board'):
            return obj.board
        if hasattr(obj, 'task') and hasattr(obj.task, 'board'):
            return obj.task.board
        return None


class IsBoardOwner(permissions.BasePermission):
    """Allow destructive actions only for board owners."""

    def has_permission(self, request, view):
        """Require authenticated users before object checks."""
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Grant access if the current user owns the task's board."""
        return obj.board is not None and obj.board.owner_id == request.user.id


class IsCommentAuthor(permissions.BasePermission):
    """Allow comment actions only for the original author."""

    def has_object_permission(self, request, view, obj):
        """Check if the comment author matches the current user."""
        return obj.author_id == request.user.id
