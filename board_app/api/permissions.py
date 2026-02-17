from rest_framework import permissions


class BoardAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        is_owner = obj.owner == user
        is_member = obj.members.filter(id=user.id).exists()

        if request.method in permissions.SAFE_METHODS or request.method == "PATCH":
            return is_owner or is_member

        return is_owner
    

