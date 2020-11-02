from django.db import models
from curricula.models import Curso, AnioLectivo
from instituciones.models import Institucion
from django.core.exceptions import ValidationError
import re

NAME_REGEX = "[A-Za-z]{2,25}( [A-Za-z]{2,25})?"


def validate_name(name):
    if not re.fullmatch(NAME_REGEX, name):
        raise ValidationError("Nombre inválido")


# nombre apellido email
class Alumno(models.Model):
    dni = models.IntegerField(blank=True)
    nombre = models.CharField(
        max_length=150, blank=True, validators=[validate_name]
    )
    apellido = models.CharField(
        max_length=150, blank=True, validators=[validate_name]
    )
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

    def clean(self):
        if self.id:
            if len(
                Alumno.objects.filter(
                    dni__exact=self.dni, institucion__exact=self.institucion
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El DNI indicado ya está en uso")

            if self.legajo and len(
                Alumno.objects.filter(
                    legajo__exact=self.legajo,
                    institucion__exact=self.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El legajo indicado ya está en uso")

            if self.email and len(
                Alumno.objects.filter(email__exact=self.email).exclude(
                    id__exact=self.id, institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El email indicado ya está en uso")
        else:
            if len(
                Alumno.objects.filter(
                    dni__exact=self.dni, institucion__exact=self.institucion
                )
            ):
                raise ValidationError("El DNI indicado ya está en uso")

            if self.legajo and len(
                Alumno.objects.filter(
                    legajo__exact=self.legajo,
                    institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El legajo indicado ya está en uso")

            if self.email and len(
                Alumno.objects.filter(
                    email__exact=self.email,
                    institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El email indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Alumno, self).save(*args, **kwargs)

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
        permissions = [
            ("list_alumnocurso", "Puede listar alumnocurso"),
            (
                "list_evaluaciones_alumnocurso",
                "Puede listar alumnocurso con evaluaciones",
            ),
            (
                "create_multiple_alumnocurso",
                "Puede crear multiples alumnocurso",
            ),
            (
                "delete_multiple_alumnocurso",
                "Puede borrar multiples alumnocurso",
            ),
        ]
