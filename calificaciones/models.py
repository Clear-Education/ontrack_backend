from django.db import models
from curricula.models import Evaluacion, Materia, AnioLectivo
from alumnos.models import Alumno


class Calificacion(models.Model):
    fecha = models.DateField(blank=True)
    puntaje = models.FloatField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    alumno = models.ForeignKey(to=Alumno, on_delete=models.CASCADE, blank=True)
    evaluacion = models.ForeignKey(
        to=Evaluacion, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return "{} {} {}".format(
            self.evaluacion.nombre + " " + self.fecha + " " + self.alumno.dni
        )

    class Meta:
        permissions = [
            ("list_calificacion", "Puede listar calificaciones"),
            ("create_multiple_calificacion", "Puede listar calificaciones"),
            (
                "destroy_multiple_calificacion",
                "Puede eliminar muchas calificaciones",
            ),
            (
                "promedio_calificacion",
                "Puede solicitar promedio de calificaciones",
            ),
        ]
