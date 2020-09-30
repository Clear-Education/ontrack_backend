from actualizaciones.api import views
from django.urls import path

urlpatterns = [
    path(
        "<int:seguimiento_pk>",
        views.create_actualizacion,
        name="actualizacion-create",
    ),
    path(
        "<int:seguimiento_pk>/list/",
        views.list_actualizacion,
        name="actualizacion-list",
    ),
    path(
        "<int:actualizacion_pk>/",
        views.mix_actualizacion,
        name="mix-actualizacion",
    ),
    path(
        "<int:actualizacion_pk>/files/",
        views.upload_file,
        name="actualizacion-upload",
    ),
]
