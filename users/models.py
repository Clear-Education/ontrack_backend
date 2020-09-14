from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    Group,
)
from django.utils import timezone
from django.db import models
from .managers import UserManager
from softdelete.models import SoftDeleteObject
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import (
    reset_password_token_created,
    post_password_reset,
)
from instituciones.models import Institucion
from django.core.exceptions import ValidationError
import re

NAME_REGEX = "[A-Za-z]{2,25}( [A-Za-z]{2,25})?"
PHONE_REGEX = "\d+"


def validate_name(name):
    if not re.fullmatch(NAME_REGEX, name):
        raise ValidationError("Nombre inválido")


def validate_phone(phone):
    if not re.fullmatch(PHONE_REGEX, phone):
        raise ValidationError("Teléfono inválido")


def validate_email(email):
    if len(User.objects.filter(email__exact=email)):
        raise ValidationError("El email indicado ya está en uso")


def validate_legajo(legajo, institucion):
    if len(
        User.objects.filter(
            legajo__exact=legajo, institucion__exact=institucion
        )
    ):
        raise ValidationError("El legajo indicado ya está en uso")


def validate_dni(dni):
    if len(User.objects.filter(dni__exact=dni)):
        raise ValidationError("El dni indicado ya está en uso")


class User(AbstractBaseUser, SoftDeleteObject, PermissionsMixin):
    email = models.EmailField(null=True)
    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre",
        validators=[validate_name],
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Teléfono",
        validators=[validate_phone],
    )
    groups = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Tipo de Cuenta",
    )
    institucion = models.ForeignKey(
        to=Institucion,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Institución",
    )
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Fecha de Nacimiento"
    )
    picture = models.FileField(
        blank=True, null=True, verbose_name="Foto de Perfil"
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    first_login = models.BooleanField(default=True)
    dni = models.IntegerField(
        primary_key=False, blank=True, null=True, verbose_name="DNI",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Apellido",
        validators=[validate_name],
    )
    cargo = models.CharField(max_length=150, blank=True, null=True)
    legajo = models.IntegerField(primary_key=False, blank=True, null=True)
    direccion = models.CharField(
        max_length=150, null=True, blank=True, verbose_name="Dirección"
    )
    localidad = models.CharField(max_length=150, null=True, blank=True)
    provincia = models.CharField(max_length=150, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def clean(self):
        if self.id:
            if len(
                User.objects.filter(email__exact=self.email).exclude(
                    id__exact=self.id
                )
            ):
                raise ValidationError("El email indicado ya está en uso")

            if (
                self.legajo
                and self.institucion
                and len(
                    User.objects.filter(
                        legajo__exact=self.legajo,
                        institucion__exact=self.institucion,
                    ).exclude(id__exact=self.id)
                )
            ):
                raise ValidationError("El legajo indicado ya está en uso")

            if self.dni and len(
                User.objects.filter(dni__exact=self.dni).exclude(
                    id__exact=self.id
                )
            ):
                raise ValidationError("El DNI indicado ya está en uso")
        else:
            if len(User.objects.filter(email__exact=self.email)):
                raise ValidationError("El email indicado ya está en uso")

            if (
                self.legajo
                and self.institucion
                and len(
                    User.objects.filter(
                        legajo__exact=self.legajo,
                        institucion__exact=self.institucion,
                    )
                )
            ):
                raise ValidationError("El legajo indicado ya está en uso")

            if self.dni and len(User.objects.filter(dni__exact=self.dni)):
                raise ValidationError("El DNI indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "Usuarios"
        permissions = [
            ("createadmin_user", "Can create users with group Admin"),
            ("status_user", "Can change status of User"),
            ("change_other_user", "Can edit other users info"),
        ]


"""
    En caso de habilitar registración por el Usuario descomentar
"""
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def _post_save_receiver(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        "current_user": reset_password_token.user,
        "email": reset_password_token.user.email,
        "reset_password_url": "{}?token={}".format(
            reverse("password_reset:reset-password-request"),
            reset_password_token.key,
        ),
    }

    # render email text
    email_html_message = render_to_string(
        "email/user_reset_password.html", context
    )
    email_plaintext_message = render_to_string(
        "email/user_reset_password.txt", context
    )

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(post_password_reset)
def password_reset_change_first_login(user, *args, **kwargs):
    """
    Sets first-login to False on user model
    """
    if user.first_login:
        user.first_login = False
        user.save()
