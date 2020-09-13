from django.db import models
from alumnos.models import AlumnoCurso
from users.models import User
from curricula.models import AnioLectivo, Materia
from instituciones.models import Institucion
from django.core.exceptions import ValidationError
from softdelete.models import SoftDeleteObject


class Seguimiento(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_cierre = models.DateField(null=True)
    descripcion = models.TextField(
        blank=True, verbose_name="Información General"
    )
    nombre = models.CharField(max_length=256)
    en_progreso = models.BooleanField()
    alumnos = models.ManyToManyField(to=AlumnoCurso)
    # Redundante ya que tiene AlumnoCurso pero por las dudas
    anio_lectivo = models.ForeignKey(to=AnioLectivo, on_delete=models.CASCADE)
    institucion = models.ForeignKey(to=Institucion, on_delete=models.CASCADE)
    materias = models.ManyToManyField(to=Materia)

    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Seguimiento.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Seguimiento.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Seguimiento, self).save(*args, **kwargs)

    class Meta:
        ordering = ["fecha_creacion"]
        verbose_name_plural = "Seguimientos"
        permissions = [
            ("status_seguimiento", "Cambiar el estado de seguimiento"),
            ("list_seguimiento", "Listar seguimiento"),
        ]


class RolSeguimiento(models.Model):
    nombre = models.CharField(max_length=256)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_rolseguimiento", "Listar integrante de seguimiento"),
        ]


class IntegranteSeguimiento(models.Model):
    fecha_hasta = models.DateField(null=True)
    fecha_desde = models.DateField(auto_now_add=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    seguimiento = models.ForeignKey(
        to=Seguimiento, related_name="integrantes", on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rol = models.ForeignKey(to=RolSeguimiento, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("list_integranteseguimiento", "Listar Integrate de Seguimiento"),
        ]


class SolicitudSeguimiento(SoftDeleteObject):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creador = models.ForeignKey(to=User, on_delete=models.CASCADE)
    alumnos = models.ManyToManyField(to=AlumnoCurso)
    motivo_solicitud = models.TextField(null=True)

    class Meta:
        permissions = [
            ("list_solicitudseguimiento", "Listar Solciitudes de Seguimiento"),
            (
                "status_solicitudseguimiento",
                "Cambiar el estado de Solciitudes de Seguimiento",
            ),
        ]


class EstadoSolicitudSeguimiento(SoftDeleteObject):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=256)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            (
                "list_estadosolicitudseguimiento",
                "Listar estados de Solicitud de Seguimiento",
            ),
        ]


class FechaEstadoSolicitudSeguimiento(SoftDeleteObject):
    fecha = models.DateTimeField(auto_now_add=True)
    solicitud = models.ForeignKey(
        SolicitudSeguimiento, on_delete=models.CASCADE, related_name="estado",
    )
    estado_solicitud = models.ForeignKey(
        EstadoSolicitudSeguimiento, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["fecha"]

        permissions = [
            (
                "list_fechaestadosolicitudseguimiento",
                "Listar Fechas de Estado Solicitud de Seguimiento",
            ),
        ]
