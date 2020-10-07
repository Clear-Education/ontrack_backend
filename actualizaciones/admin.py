from django.contrib import admin
from actualizaciones.models import Actualizacion, ActualizacionAdjunto
from ontrack import settings

if settings.DEVELOPER_ADMIN:
    admin.site.register(Actualizacion)
    admin.site.register(ActualizacionAdjunto)

