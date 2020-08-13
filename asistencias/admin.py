from django.contrib import admin
from asistencias.models import Asistencia
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Asistencia)
