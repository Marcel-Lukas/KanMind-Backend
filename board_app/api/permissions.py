"""Custom permission rules for board access."""

from rest_framework import permissions


class BoardAccessPermission(permissions.BasePermission):
    """Allow members to read/update; only owners may delete."""

    # HTTP methods that members (in addition to owners) may perform.
    MEMBER_WRITE_METHODS = ('PATCH',)

    def has_object_permission(self, request, view, obj):
        """Apply object-level access based on board role and HTTP method."""
        user = request.user
        is_owner = obj.owner_id == user.id
        is_member = obj.members.filter(id=user.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_owner or is_member
        if request.method in self.MEMBER_WRITE_METHODS:
            return is_owner or is_member
        return is_owner
