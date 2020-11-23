from os import name
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User
from django_rest_passwordreset.models import ResetPasswordToken
from softdelete.models import ChangeSet, SoftDeleteRecord
from rest_framework.authtoken.models import Token
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

class UsuarioForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['last_name'].required = True
        self.fields['groups'].required = True
        self.fields['institucion'].required = True


class UserAdmin(BaseUserAdmin):

    form = UsuarioForm
    add_form = UsuarioForm

    list_display = (
        "email",
        "name",
        "last_name",
        "institucion",
        "groups",
    )
    list_filter = ("is_superuser",)

    fieldsets = (
        (None, {"fields": ("email", "is_active",)},),
        ("Información Personal", {"fields": ("name", "last_name",)},),
        ("Información Insititucional", {"fields": ("groups", "institucion",)}),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2",)},),
        ("Información Personal", {"fields": ("name", "last_name",)},),
        ("Información Insititucional", {"fields": ("groups", "institucion",)}),
    )

    search_fields = ("email", "name", "last_name", "institucion")
    ordering = ("email",)
    list_filter = ()
    filter_horizontal = ()

    


admin.site.register(User, UserAdmin)
admin.site.unregister(ResetPasswordToken)
admin.site.unregister(ChangeSet)
admin.site.unregister(SoftDeleteRecord)
admin.site.unregister(Token)

