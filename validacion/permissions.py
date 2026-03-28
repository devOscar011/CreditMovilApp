from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class GroupPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # ADMIN → Todo permitido
        if user.groups.filter(name="Admin").exists():
            return True

        # ANALISTA → Todo excepto DELETE
        if user.groups.filter(name="Analista").exists():
            if request.method == "DELETE":
                return False
            return True


        # PROMOTOR → Puede ver y editar (PUT/PATCH)
        if user.groups.filter(name="Promotor").exists():
            if request.method in ["GET", "HEAD", "OPTIONS", "POST"]:
                return True
            return False

        # Sin grupo → no autorizado
        return False

class IsAdminGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()
