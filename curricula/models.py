from django.db import models
from instituciones.models import Institucion
from django.core.exceptions import ValidationError


class Carrera(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=False)
    institucion = models.ForeignKey(to=Institucion, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=150)

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Carrera.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Carrera.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Carrera, self).save(*args, **kwargs)

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

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Anio.objects.filter(
                    nombre__exact=self.nombre,
                    carrera__institucion__exact=self.carrera.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Anio.objects.filter(
                    nombre__exact=self.nombre,
                    carrera__institucion__exact=self.carrera.institucion,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Anio, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_anio", "Puede listar anio"),
        ]


class Curso(models.Model):
    nombre = models.CharField(max_length=150)
    anio = models.ForeignKey(
        to=Anio, related_name="cursos", on_delete=models.CASCADE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Curso.objects.filter(
                    nombre__exact=self.nombre,
                    anio__carrera__institucion__exact=self.anio.carrera.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Curso.objects.filter(
                    nombre__exact=self.nombre,
                    anio__carrera__institucion__exact=self.anio.carrera.institucion,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Curso, self).save(*args, **kwargs)

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

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Materia.objects.filter(
                    nombre__exact=self.nombre,
                    anio__carrera__exact=self.anio.carrera,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Materia.objects.filter(
                    nombre__exact=self.nombre,
                    anio__carrera__exact=self.anio.carrera,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Materia, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_materia", "Puede listar materias"),
        ]


class AnioLectivo(models.Model):
    nombre = models.CharField(max_length=150, primary_key=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_desde = models.DateField(blank=True)
    fecha_hasta = models.DateField(blank=True)
    institucion = models.ForeignKey(
        to=Institucion, on_delete=models.CASCADE, blank=True
    )

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                AnioLectivo.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                AnioLectivo.objects.filter(
                    nombre__exact=self.nombre,
                    institucion__exact=self.institucion,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(AnioLectivo, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_aniolectivo", "Puede listar años lectivos"),
            ("actual_aniolectivo", "Puede ver el año lectivo actual"),
        ]


class Evaluacion(models.Model):
    nombre = models.CharField(max_length=150)
    materia = models.ForeignKey(
        to=Materia,
        related_name="evaluaciones",
        on_delete=models.CASCADE,
        default=None,
    )
    anio_lectivo = models.ForeignKey(
        to=AnioLectivo,
        related_name="evaluaciones",
        on_delete=models.CASCADE,
        default=None,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha = models.DateField(blank=True, null=True)
    ponderacion = models.FloatField(blank=False)

    def clean(self):
        if not self.nombre:
            raise ValidationError("Es necesario ingresar un nombre")
        self.nombre = self.nombre.upper()
        if self.id:
            if len(
                Evaluacion.objects.filter(
                    nombre__exact=self.nombre,
                    materia__exact=self.materia,
                    anio_lectivo__exact=self.anio_lectivo,
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError("El nombre indicado ya está en uso")
        else:
            if len(
                Evaluacion.objects.filter(
                    nombre__exact=self.nombre,
                    materia__exact=self.materia,
                    anio_lectivo__exact=self.anio_lectivo,
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Evaluacion, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = [
            ("list_evaluacion", "Puede listar evaluaciones"),
        ]
