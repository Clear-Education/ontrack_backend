from django.urls import path
from curricula.api.views import carrera, anio_lectivo, anio, materia

urlpatterns = [
    path("carrera/", carrera.create_carrera, name="carrera-create"),
    path(
        "carrera/<int:pk>/",
        carrera.view_edit_carrera,
        name="carrera-view-edit",
    ),
    path("carrera/list/", carrera.list_carrera, name="carrera-list"),
    path("anio/", anio.create_anio, name="anio-create"),
    path("anio/<int:pk>/", anio.view_edit_anio, name="anio-view-edit"),
    path(
        "carrera/<int:carrera_id>/anio/list/",
        anio.list_anio,
        name="carrera-list",
    ),
    path("curso/<int:pk>/", anio.view_edit_curso, name="curso-view-edit"),
    path(
        "materia/<int:pk>/",
        materia.view_edit_materia,
        name="materia-view-edit",
    ),
    path("materia/list/", materia.list_materia, name="materia-list"),
    path("materia/", materia.create_materia, name="materia-create"),
    path(
        "anio_lectivo/",
        anio_lectivo.create_anio_lectivo,
        name="anio-lectivo-create",
    ),
    path(
        "anio_lectivo/list/",
        anio_lectivo.list_anio_lectivo,
        name="anio-lectivo-list",
    ),
    path(
        "anio_lectivo/<int:pk>/",
        anio_lectivo.update_anio_lectivo,
        name="anio-lectivo-update",
    ),
]
