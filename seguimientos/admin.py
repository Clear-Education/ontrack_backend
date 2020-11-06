from django.contrib import admin
from ontrack import settings
from seguimientos.models import (
    Seguimiento,
    RolSeguimiento,
    IntegranteSeguimiento,
    SolicitudSeguimiento,
)

# Register your models here.
if settings.DEVELOPER_ADMIN:
    admin.site.register(Seguimiento)
    admin.site.register(RolSeguimiento)
    admin.site.register(IntegranteSeguimiento)
    admin.site.register(SolicitudSeguimiento)
