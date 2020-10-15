from django.db import models
from django.core.exceptions import ValidationError

from users.models import User
from seguimientos.models import Seguimiento


class Actualizacion(models.Model):
    cuerpo = models.CharField(max_length=500, null=False, blank=False)
    padre = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="comentarios",
        blank=True,
        null=True,
    )
    seguimiento = models.ForeignKey(
        to=Seguimiento, on_delete=models.CASCADE, blank=True, null=False
    )
    usuario = models.ForeignKey(
        to=User, on_delete=models.CASCADE, blank=True, null=False
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return (
            self.seguimiento.nombre
            + " "
            + self.usuario.name
            + " "
            + str(self.pk)
        )

    class Meta:
        permissions = [
            ("list_actualizacion", "Puede listar actualizaciones"),
            (
                "list_latest_actualizacion",
                "Puede listar las ultimas actualizaciones",
            ),
        ]


def seguimiento_file_path(instance, filename):
    return f"seguimiento_{str(instance.actualizacion.seguimiento.id)}/actualizacion_{instance.actualizacion.id}/{filename}"


def validate_file_size(value):
    filesize = value.size

    if filesize > 10485760:
        raise ValidationError("El tamaño máximo de un archivo es 10MB")
    else:
        return value


class ActualizacionAdjunto(models.Model):
    actualizacion = models.ForeignKey(
        to=Actualizacion,
        on_delete=models.CASCADE,
        related_name="adjuntos",
        blank=False,
        null=False,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.FileField(
        blank=False,
        null=False,
        upload_to=seguimiento_file_path,
        validators=[validate_file_size],
    )
    upload_name = models.CharField(max_length=500, null=False, blank=True)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.IntegerField(blank=True)

    def __str__(self):
        return str(self.pk)
