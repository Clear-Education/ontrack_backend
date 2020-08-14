from django.contrib import admin
from calificaciones.models import Calificacion
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Calificacion)
