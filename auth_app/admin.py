"""Admin configuration for the built-in User and DRF Token models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.admin import TokenAdmin as DRFTokenAdmin
from rest_framework.authtoken.models import TokenProxy


# Re-register both models so we can customise their admin pages.
for _model in (User, TokenProxy):
    try:
        admin.site.unregister(_model)
    except admin.sites.NotRegistered:
        pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """User admin with extra columns and search fields."""

    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'is_staff', 'is_active',
    )
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    ordering = ('-id',)


@admin.register(TokenProxy)
class CustomTokenAdmin(DRFTokenAdmin):
    """Token admin extended with a sortable user-id column."""

    list_display = ('user_id_display', 'key', 'user', 'created')
    search_fields = tuple(DRFTokenAdmin.search_fields) + ('user__id',)
    ordering = ('-user__id',)

    @admin.display(description='User ID', ordering='user__id')
    def user_id_display(self, obj):
        """Return the user id for the list display column."""
        return obj.user_id
