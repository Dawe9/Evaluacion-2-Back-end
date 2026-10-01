"""Administración del catálogo, las cuentas y solicitudes de farmacia."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    Cart,
    CartItem,
    Institution,
    MedicalSupply,
    Profile,
    PurchaseRequest,
    PurchaseRequestItem,
    SupplyCategory,
)


class ProfileInline(admin.StackedInline):
    """Permite al superusuario asignar roles y a staff vincular instituciones."""

    model = Profile
    extra = 1
    can_delete = False

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('role', 'institution')
        return ('institution',)


admin.site.unregister(User)


@admin.register(User)
class PageUserAdmin(UserAdmin):
    """Reserva la promoción a staff/superuser al superadministrador."""

    inlines = [ProfileInline]
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(is_staff=False, is_superuser=False)

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        if not request.user.is_active or not request.user.is_staff:
            return False
        return request.user.is_superuser or obj is None or not (obj.is_staff or obj.is_superuser)

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if not request.user.is_active or not request.user.is_staff:
            return False
        return request.user.is_superuser or obj is None or not (obj.is_staff or obj.is_superuser)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_active or not request.user.is_staff:
            return False
        return request.user.is_superuser or obj is None or not (obj.is_staff or obj.is_superuser)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        if obj is None:
            return ((None, {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email'),
            }),)
        return (
            (None, {'fields': ('username',)}),
            ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not request.user.is_superuser:
            Profile.objects.get_or_create(
                user=form.instance,
                defaults={'role': Profile.Role.MEDICAL_INSTITUTION},
            )


class WarehouseStaffAdmin(admin.ModelAdmin):
    """Permite CRUD de catálogo a administradores de página asignados por staff."""

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


class WarehouseReadOnlyAdmin(admin.ModelAdmin):
    """Permite al staff revisar solicitudes sin saltarse su flujo transaccional."""

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id')
    search_fields = ('name', 'tax_id')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'institution')
    list_filter = ('role', 'institution')
    search_fields = ('user__username', 'institution__name')


@admin.register(SupplyCategory)
class SupplyCategoryAdmin(WarehouseStaffAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(MedicalSupply)
class MedicalSupplyAdmin(WarehouseStaffAdmin):
    list_display = (
        'commercial_name', 'active_ingredient', 'category', 'lot',
        'expiration_date', 'unit_price', 'stock', 'is_active',
    )
    list_filter = ('category', 'is_active', 'expiration_date')
    search_fields = ('commercial_name', 'active_ingredient', 'lot')


class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    extra = 0
    can_delete = False
    readonly_fields = ('supply', 'supply_name', 'lot', 'quantity', 'unit_price')


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(WarehouseReadOnlyAdmin):
    list_display = ('id', 'institution', 'status', 'total', 'created_at')
    list_filter = ('status', 'institution', 'created_at')
    readonly_fields = ('institution', 'created_by', 'status', 'total', 'created_at', 'updated_at')
    inlines = [PurchaseRequestItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    readonly_fields = ('user', 'updated_at')
    inlines = []


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'supply', 'quantity')
    list_select_related = ('cart', 'supply')
