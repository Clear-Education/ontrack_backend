from django.db import models

# Create your models here.
class Asistencia(models.Model):
    fecha = models.DateField(blank=True)
    asistio = models.FloatField(blank=True)
    descripcion = models.CharField(max_lengt=150, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    alumno = models.ForeignKey(to=Alumno, on_delete=models.CASCADE, blank=True)
    anio_lectivo = models.ForeignKey(
        to=AnioLectivo, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return self.alumno.nombre + " " + self.fecha

    class Meta:
        permissions = [("list_asistencia", "Puede listar asistencias")]


class AsistenciaAnioLectivo(models.Model):
    porcentaje = models.FloatField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    alumno = models.ForeignKey(to=Alumno, on_delete=models.CASCADE, blank=True)
    anio_lectivo = models.ForeignKey(
        to=AnioLectivo, on_delete=models.CASCADE, blank=True
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
