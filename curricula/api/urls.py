from curricula.api import views
from django.urls import path

urlpatterns = [
    path("carrera/", views.create_carrera, name="carrera-create"),
    path(
        "carrera/<int:pk>/", views.view_edit_carrera, name="carrera-view-edit"
    ),
    path("carrera/list/", views.list_carrera, name="carrera-list"),
    path("anio/", views.create_anio, name="anio-create"),
    path("anio/<int:pk>/", views.view_edit_anio, name="anio-view-edit"),
    path(
        "carrera/<int:carrera_id>/anio/list/",
        views.list_anio,
        name="carrera-list",
    ),
    path("curso/<int:pk>/", views.view_edit_curso, name="curso-view-edit"),
]
