from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


class UserAdmin(BaseUserAdmin):

    list_display = ("email", "name", "phone", "date_of_birth", "is_staff", "is_active", "institucion", "groups")
    list_filter = ("is_superuser",)

    fieldsets = (
        (None, {"fields": ("email", "is_staff", "is_superuser", "is_active", "password")}),
        ("Personal info", {"fields": ("name", "phone", "date_of_birth", "picture")}),
        ("Groups", {"fields": ("groups", "institucion")}),
        ("Permissions", {"fields": ("user_permissions",)}),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "is_staff", "is_superuser", "password1", "password2")}),
        ("Personal info", {"fields": ("name", "phone", "date_of_birth", "picture")}),
        ("Groups", {"fields": ("groups", "institucion")}),
        ("Permissions", {"fields": ("user_permissions",)}),
    )

    search_fields = ("email", "name", "phone")
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

