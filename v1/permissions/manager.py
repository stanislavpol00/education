from rest_framework.permissions import BasePermission


class IsManagerUser(BasePermission):
    """
    Allows access only to authenticated managers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_manager
        )
