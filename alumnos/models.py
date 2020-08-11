from django.db import models
from curricula.models import Curso, AnioLectivo
from instituciones.models import Institucion


class Alumno(models.Model):
    dni = models.IntegerField(unique=True, primary_key=False, blank=True)
    nombre = models.CharField(max_length=150, blank=True)
    apellido = models.CharField(max_length=150, blank=True)
    email = models.EmailField(null=True, blank=True)
    legajo = models.CharField(max_length=150, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=150, null=True, blank=True)
    localidad = models.CharField(max_length=150, null=True, blank=True)
    provincia = models.CharField(max_length=150, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    fecha_inscripcion = models.DateField(null=True, blank=True)
    institucion = models.ForeignKey(
        to=Institucion, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return self.nombre + " " + self.apellido

    class Meta:
        permissions = [("list_alumno", "Puede listar alumnos")]


class AlumnoCurso(models.Model):
    alumno = models.ForeignKey(to=Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(to=Curso, on_delete=models.CASCADE)
    anio_lectivo = models.ForeignKey(to=AnioLectivo, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alumno.nombre + " del curso " + self.curso.nombre

    class Meta:
        permissions = [("list_alumnocurso", "Puede listar alumnocurso")]
