from asistencias.api import views
from django.urls import path

urlpatterns = [
    path("", views.create_asistencia, name="asistencia-create-delete-curso",),
    path(
        "multiple/",
        views.mix_asistencia_multiple,
        name="asistencia-create-multiple",
    ),
    path("<int:pk>/", views.mix_asistencia, name="asistencia-mix"),
    path("list/", views.list_asistencia, name="asistencia-list"),
    path(
        "stats/hoy/",
        views.hoy_asistencia_anio_lectivo,
        name="asistencia-anio-lectivo-hoy",
    ),
]
