from rest_framework.permissions import BasePermission
from .models import UserRole


class HasRolePermission(BasePermission):
    def has_permission(self, request, view):
        required = getattr(view, 'required_roles', None)
        if not required:
            return True
        user = request.user
        try:
            roles = [ur.role.role_key for ur in UserRole.objects.filter(user=user).select_related('role')]
        except Exception:
            roles = []
        return any(r in roles for r in required) or ('admin' in roles)