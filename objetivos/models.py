from django.db import models
from alumnos.models import AlumnoCurso
from seguimientos.models import Seguimiento


class TipoObjetivo(models.Model):
    nombre = models.CharField(max_length=150, blank=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    cuantitativo = models.BooleanField(blank=True)
    multiple = models.BooleanField(blank=True)
    valor_minimo = models.FloatField(blank=True, null=True)
    valor_maximo = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Objetivos"
        verbose_name = "Tipo de Objetivo"
        permissions = [
            ("list_tipo_objetivo", "Puede listar tipo_objetivo"),
        ]


class Objetivo(models.Model):
    valor_objetivo_cuantitativo = models.FloatField(blank=True, null=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    seguimiento = models.ForeignKey(
        to=Seguimiento, on_delete=models.CASCADE, blank=True
    )
    tipo_objetivo = models.ForeignKey(
        to=TipoObjetivo, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return f"{self.seguimiento.nombre}--{self.id}: tipo({self.tipo_objetivo}). {self.descripcion if self.descripcion else ''}"

    class Meta:
        permissions = [
            ("list_objetivo", "Puede listar objetivos"),
            ("create_multiple_objetivo", "Puede crear multiples objetivos"),
        ]


class AlumnoObjetivo(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    fecha_relacionada = models.DateField(null=True, blank=True)
    objetivo = models.ForeignKey(
        to=Objetivo, on_delete=models.CASCADE, blank=True
    )
    alumno_curso = models.ForeignKey(
        to=AlumnoCurso, on_delete=models.CASCADE, blank=True
    )
    valor = models.FloatField(blank=True, null=True)
    alcanzada = models.BooleanField(blank=True)

    def __str__(self):
        return f"{self.objetivo.seguimiento.nombre}: tipo({self.objetivo.tipo_objetivo}). {self.alumno_curso.alumno}"

    class Meta:
        permissions = [
            ("list_alumno_objetivo", "Puede listar alumno_objetivo"),
        ]
