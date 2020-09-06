from django.contrib import admin
from objetivos.models import Objetivo, AlumnoObjetivo, TipoObjetivo
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Objetivo)
    admin.site.register(AlumnoObjetivo)

admin.site.register(TipoObjetivo)
