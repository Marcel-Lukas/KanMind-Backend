"""Custom permission classes for task and comment access."""

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from tasks_app.models import Task
from board_app.models import Board


class IsMemberOfBoard(permissions.BasePermission):
    """Allow access only to board members or owners."""

    def has_permission(self, request, view):
        """Validate board access for non-object requests."""
        board = self._get_board(request, view, from_object=False)
        return board is not None and self._is_member_or_owner(request.user, board)

    def has_object_permission(self, request, view, obj):
        """Validate board access for object-level requests."""
        board = self._get_board(request, view, obj=obj, from_object=True)
        return board is not None and self._is_member_or_owner(request.user, board)

    def _get_board(self, request, view, obj=None, from_object=False):
        """Resolve board from object, request data, or route params."""
        if from_object and obj:
            return self._extract_board_from_object(obj)

        board_id = self._get_board_id_from_data(request)
        if board_id:
            return get_object_or_404(Board, pk=board_id)

        task_id = view.kwargs.get("pk") or view.kwargs.get("task_id")
        if task_id:
            task = get_object_or_404(Task, pk=task_id)
            return task.board

        return None

    def _get_board_id_from_data(self, request):
        """Support common board field names in incoming payloads."""
        data = getattr(request, "data", {}) or {}
        return data.get("board") or data.get("board_id") or data.get("boardId")

    def _extract_board_from_object(self, obj):
        """Extract board relation from task or comment objects."""
        if hasattr(obj, "board"):
            return obj.board
        if hasattr(obj, "task") and hasattr(obj.task, "board"):
            return obj.task.board
        return None

    def _is_member_or_owner(self, user, board):
        """Return ``True`` if user owns or joined the board."""
        return board.owner_id == user.id or board.members.filter(id=user.id).exists()



class IsBoardOwner(permissions.BasePermission):
    """Allow destructive actions only for board owners."""

    def has_permission(self, request, view):
        """Require authenticated users before object checks."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Grant access if current user owns the task's board."""
        user = request.user
        return self._is_board_owner(user, obj.board)
    
    def _is_board_owner(self, user, board):
        """Compare current user with board owner."""
        return board.owner_id == user.id



class IsCommentAuthor(permissions.BasePermission):
    """Allow comment actions only for the original author."""

    def has_object_permission(self, request, view, obj):
        """Check if comment author matches current user."""
        return obj.author == request.user
    

