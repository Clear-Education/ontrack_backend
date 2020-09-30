from django.db import models

from users.models import User
from seguimientos.models import Seguimiento


class Actualizacion(models.Model):
    cuerpo = models.CharField(max_length=500, null=False, blank=False)
    padre = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="hijo",
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
            self.seguimiento.nombre + " " + self.usuario.name + " " + self.pk
        )

    class Meta:
        permissions = [("list_actualizacion", "Puede listar actualizaciones")]


class ActualizacionAdjunto(models.Model):
    actualizacion = models.ForeignKey(
        to=Actualizacion,
        on_delete=models.CASCADE,
        related_name="adjuntos",
        blank=False,
        null=False,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    url = models.URLField(blank=False, null=False)

    def __str__(self):
        return self.actualizacion + " " + self.url
