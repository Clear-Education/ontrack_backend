from django.db import models
from alumnos.models import AlumnoCurso
from users.models import User
from curricula.models import AnioLectivo, Materia
from instituciones.models import Institucion


class Seguimiento(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    descripcion = models.TextField(
        blank=True, verbose_name="Información General"
    )
    nombre = models.CharField(max_length=256)
    en_progreso = models.BooleanField()
    alumnos = models.ManyToManyField(to=AlumnoCurso)
    encargado = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # Redundante ya que tiene AlumnoCurso pero por las dudas
    anio_lectivo = models.ForeignKey(to=AnioLectivo, on_delete=models.CASCADE)
    institucion = models.ForeignKey(to=Institucion, on_delete=models.CASCADE)
    materias = models.ManyToManyField(to=Materia)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["fecha_creacion"]
        verbose_name_plural = "Seguimientos"
        permissions = [
            ("status_seguimiento", "Cambiar el estado de seguimiento"),
            ("list_seguimiento", "Listar seguimiento"),
        ]


class RolSeguimiento(models.Model):
    nombre = models.CharField(max_length=256)

    def __str__(self):
        return self.nombre

    permissions = [
        ("list_rolseguimiento", "Listar integrante de seguimiento"),
    ]


class IntegranteSeguimiento(models.Model):
    fecha_hasta = models.DateField(null=True)
    fecha_desde = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    seguimiento = models.ForeignKey(to=Seguimiento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rol = models.ForeignKey(to=RolSeguimiento, on_delete=models.CASCADE)

    permissions = [
        ("list_integranteseguimiento", "Listar Integrate de Seguimiento"),
    ]