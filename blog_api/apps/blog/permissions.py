from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Owner can change,
    for other only read.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user