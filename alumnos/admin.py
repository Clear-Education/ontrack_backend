from django.contrib import admin
from alumnos.models import Alumno, AlumnoCurso
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Alumno)
    admin.site.register(AlumnoCurso)

