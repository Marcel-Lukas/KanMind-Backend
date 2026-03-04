"""Custom permission rules for board access."""

from rest_framework import permissions


class BoardAccessPermission(permissions.BasePermission):
    """Allow members to read/update; only owners may delete."""

    def has_object_permission(self, request, view, obj):
        """Apply object-level access based on board role and HTTP method."""
        user = request.user

        is_owner = obj.owner == user
        is_member = obj.members.filter(id=user.id).exists()

        if request.method in permissions.SAFE_METHODS or request.method == "PATCH":
            return is_owner or is_member

        return is_owner
    

