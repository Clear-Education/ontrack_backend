from django.db import models
from instituciones.models import Institucion


class Carrera(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=False)
    institucion = models.ForeignKey(to=Institucion, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_carrera", "Puede listar carreras"),
        ]


class Anio(models.Model):
    nombre = models.CharField(max_length=150)
    carrera = models.ForeignKey(to=Carrera, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_anio", "Puede listar anio"),
        ]


class Curso(models.Model):
    nombre = models.CharField(max_length=150)
    anio = models.ForeignKey(to=Anio, related_name="cursos", on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_curso", "Puede listar cursos"),
        ]


class Materia(models.Model):
    nombre = models.CharField(max_length=150)
    anio = models.ForeignKey(to=Anio, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_materia", "Puede listar materias"),
        ]


class MateriaEvaluacion(models.Model):
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_baja = models.DateTimeField(blank=True)
    materia = models.ForeignKey(to=Materia, on_delete=models.CASCADE)


class Evaluacion(models.Model):
    nombre = models.CharField(max_length=150)
    materia_evaluacion = models.ForeignKey(
        to=MateriaEvaluacion, related_name="evaluaciones", on_delete=models.CASCADE, null=True,  # Only for now
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ponderacion = models.FloatField(blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_evaluacion", "Puede listar evaluaciones"),
        ]


class AnioLectivo(models.Model):
    nombre = models.CharField(max_length=150, unique=True, primary_key=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_desde = models.DateField(blank=True)
    fecha_hasta = models.DateField(blank=True)
    institucion = models.ForeignKey(to=Institucion, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_aniolectivo", "Puede listar años lectivos"),
        ]

