from django.db import models

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

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["fecha_creacion"]
        verbose_name_plural = "Instituciones"
        permissions = [
            ("status_institucion", "Cambiar el estado Instituciones"),
            ("list_institucion", "Puede listar Instituciones"),
        ]
