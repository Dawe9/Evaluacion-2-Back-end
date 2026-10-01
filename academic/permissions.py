"""Permisos basados en el rol persistido del perfil autenticado."""

from rest_framework.permissions import BasePermission

from .models import Profile


class IsWarehouseManager(BasePermission):
    """Permite cambios de inventario y estados solo al gestor de bodega."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and Profile.objects.filter(
                user=request.user,
                role=Profile.Role.WAREHOUSE_MANAGER,
            ).exists()
        )


class IsMedicalInstitution(BasePermission):
    """Limita carros y solicitudes a cuentas de instituciones médicas."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_staff
            and Profile.objects.filter(
                user=request.user,
                role=Profile.Role.MEDICAL_INSTITUTION,
            ).exists()
        )