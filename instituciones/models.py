from django.db import models


class Institucion(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100, null=False, default="")
    direccion = models.CharField(max_length=250, blank=True)
    pais = models.CharField(max_length=250, blank=True)
    identificador = models.CharField(max_length=250, blank=True)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    activa = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["fecha_creacion"]
        permissions = [
            ("status_institucion", "Cambiar el estado Instituciones"),
            ("list_institucion", "Puede listar Instituciones"),
        ]
