from rest_framework.permissions import BasePermission


class IsAdminOrSuperAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol admin o super_admin."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and hasattr(user, "perfil")
            and user.perfil.rol in ("admin", "super_admin")
        )
