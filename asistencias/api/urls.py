from asistencias.api import views
from django.urls import path

urlpatterns = [
    path(
        "",
        views.create_delete_curso_asistencia,
        name="asistencia-create-delete-curso",
    ),
    path(
        "multiple/",
        views.create_asistencia_multiple,
        name="asistencia-create-multiple",
    ),
    path("<int:pk>/", views.mix_asistencia, name="asistencia-mix"),
    path("list/", views.list_asistencia, name="asistencia-list"),
    path(
        "stats/list/",
        views.list_asistencia_anio_lectivo,
        name="asistencia-anio-lectivo-list",
    ),
    path(
        "stats/hoy/",
        views.hoy_asistencia_anio_lectivo,
        name="asistencia-anio-lectivo-hoy",
    ),
]
