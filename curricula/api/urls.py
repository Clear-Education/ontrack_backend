from django.urls import path
from curricula.api.views import (
    carrera,
    anio_lectivo,
    anio,
    materia,
    evaluacion,
)

urlpatterns = [
    # Carrera
    path("carrera/", carrera.create_carrera, name="carrera-create"),
    path(
        "carrera/<int:pk>/",
        carrera.view_edit_carrera,
        name="carrera-view-edit",
    ),
    path("carrera/list/", carrera.list_carrera, name="carrera-list"),
    # Año
    path("anio/", anio.create_anio, name="anio-create"),
    path("anio/<int:pk>/", anio.view_edit_anio, name="anio-view-edit"),
    # TODO : Decidir que hacer con este list
    path(
        "carrera/<int:carrera_id>/anio/list/",
        anio.list_anio,
        name="carrera-list",
    ),
    # Curso
    path("curso/<int:pk>/", anio.view_edit_curso, name="curso-view-edit"),
    path("anio/<int:anio_id>/curso/list/", anio.list_curso, name="curso-list"),
    # Materia
    path(
        "materia/<int:pk>/",
        materia.view_edit_materia,
        name="materia-view-edit",
    ),
    path(
        "anio/<int:anio_id>/materia/list/",
        materia.list_materia,
        name="materia-list",
    ),
    path("materia/", materia.create_materia, name="materia-create"),
    # Evaluacion
    path(
        "materia/<int:materia_id>/evaluacion/list/",
        evaluacion.list_evaluacion,
        name="evaluacion-list",
    ),
    path(
        "evaluacion/<int:pk>/",
        evaluacion.view_evaluacion,
        name="evaluacion-view-edit",
    ),
    path(
        "evaluacion/", evaluacion.create_evaluacion, name="evaluacion-create",
    ),
    # Año Lectivo
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
