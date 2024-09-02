from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                return True
            if request.method == 'POST':
                return True
            if request.method == 'DELETE':
                return True
            if request.method == 'PUT':
                return True
        return False
