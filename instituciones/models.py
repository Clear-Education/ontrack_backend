from django.db import models
from django.core.exceptions import ValidationError

PAIS_CHOICES = [
    ("AR", "Argentina"),
    ("UR", "Uruguay"),
    ("CH", "Chile"),
    ("BR", "Brasil"),
    ("BV", "Bolivia"),
    ("PE", "Peru"),
    ("PG", "Paraguay"),
]


class Institucion(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100, null=False, default="")
    direccion = models.CharField(
        max_length=250, blank=True, verbose_name="Dirección"
    )
    pais = models.CharField(
        max_length=250, blank=True, verbose_name="País", choices=PAIS_CHOICES
    )
    cuit = models.BigIntegerField(verbose_name="CUIT", blank=True, null=True)
    identificador = models.CharField(max_length=250, blank=True)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    logo = models.ImageField(blank=True, null=True)
    activa = models.BooleanField(null=False, default=True)

    def clean(self):
        self.nombre = self.nombre.upper()
        if not self.cuit:
            raise ValidationError("Es necesario ingresar la CUIT")
        if self.id:
            if self.identificador and len(
                Institucion.objects.filter(
                    identificador__exact=self.identificador
                ).exclude(id__exact=self.id)
            ):
                raise ValidationError(
                    "El identificador indicado ya está en uso"
                )

            if self.nombre and len(
                Institucion.objects.filter(nombre__exact=self.nombre,).exclude(
                    id__exact=self.id
                )
            ):
                raise ValidationError("El nombre indicado ya está en uso")

            if len(
                Institucion.objects.filter(cuit__exact=self.cuit,).exclude(
                    id__exact=self.id
                )
            ):
                raise ValidationError("La CUIT indicado ya está en uso")
        else:
            if self.identificador and len(
                Institucion.objects.filter(
                    identificador__exact=self.identificador
                )
            ):
                raise ValidationError(
                    "El identificador indicado ya está en uso"
                )

            if self.nombre and len(
                Institucion.objects.filter(nombre__exact=self.nombre)
            ):
                raise ValidationError("El nombre indicado ya está en uso")

            if len(Institucion.objects.filter(cuit__exact=self.cuit)):
                raise ValidationError("La CUIT indicado ya está en uso")

    def save(self, *args, **kwargs):
        self.clean()
        return super(Institucion, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["fecha_creacion"]
        verbose_name_plural = "Instituciones"
        permissions = [
            ("status_institucion", "Cambiar el estado Instituciones"),
            ("list_institucion", "Puede listar Instituciones"),
        ]
