from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User
from django_rest_passwordreset.models import ResetPasswordToken
from softdelete.models import ChangeSet, SoftDeleteRecord
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group


class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "name",
        "last_name",
        "institucion",
        "groups",
    )
    list_filter = ("is_superuser",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "password",
                )
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "last_name",
                    "phone",
                    "date_of_birth",
                    "picture",
                    "provincia",
                    "localidad",
                    "direccion",
                )
            },
        ),
        ("Groups", {"fields": ("groups", "institucion", "legajo", "cargo")}),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2",)},),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "last_name",
                    "phone",
                    "date_of_birth",
                    "picture",
                    "provincia",
                    "localidad",
                    "direccion",
                )
            },
        ),
        ("Groups", {"fields": ("groups", "institucion", "legajo", "cargo")}),
    )

    search_fields = ("email", "name", "last_name", "institucion")
    ordering = ("email",)
    list_filter = ()
    filter_horizontal = ()


# admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.unregister(ResetPasswordToken)
admin.site.unregister(ChangeSet)
admin.site.unregister(SoftDeleteRecord)
admin.site.unregister(Token)

