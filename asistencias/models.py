from django.db import models
from alumnos.models import AlumnoCurso

# Create your models here.
class Asistencia(models.Model):
    fecha = models.DateField(blank=True)
    asistio = models.FloatField(blank=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    alumno_curso = models.ForeignKey(
        to=AlumnoCurso, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return self.alumno.nombre + " " + self.fecha

    class Meta:
        permissions = [
            ("list_asistencia", "Puede listar asistencias"),
            (
                "create_multiple_asistencia",
                "Puede crear multiples asistencias",
            ),
            (
                "destroy_curso_dia_asistencia",
                "Puede borrar multiples asistencias",
            ),
        ]


class AsistenciaAnioLectivo(models.Model):
    porcentaje = models.FloatField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    alumno_curso = models.ForeignKey(
        to=AlumnoCurso, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return self.alumno.nombre + " " + self.fecha_creacion

    class Meta:
        permissions = [
            (
                "list_asistenciaaniolectivo",
                "Puede listar asistencia_anio_lectivo",
            )
        ]
