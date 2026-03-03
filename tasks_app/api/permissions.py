from django.shortcuts import get_object_or_404
from rest_framework import permissions
from tasks_app.models import Task
from board_app.models import Board


class IsMemberOfBoard(permissions.BasePermission):
    def has_permission(self, request, view):
        board = self._get_board(request, view, from_object=False)
        return board is not None and self._is_member_or_owner(request.user, board)

    def has_object_permission(self, request, view, obj):
        board = self._get_board(request, view, obj=obj, from_object=True)
        return board is not None and self._is_member_or_owner(request.user, board)

    def _get_board(self, request, view, obj=None, from_object=False):
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
        data = getattr(request, "data", {}) or {}
        return data.get("board") or data.get("board_id") or data.get("boardId")

    def _extract_board_from_object(self, obj):
        if hasattr(obj, "board"):
            return obj.board
        if hasattr(obj, "task") and hasattr(obj.task, "board"):
            return obj.task.board
        return None

    def _is_member_or_owner(self, user, board):
        return board.owner_id == user.id or board.members.filter(id=user.id).exists()


