from django.contrib import admin
from curricula.models import Carrera, Anio, Curso, Materia, AnioLectivo
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Carrera)
    admin.site.register(Curso)
    admin.site.register(Anio)
    admin.site.register(Materia)
    admin.site.register(AnioLectivo)
