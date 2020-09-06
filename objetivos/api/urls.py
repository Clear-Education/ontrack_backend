from objetivos.api import views
from django.urls import path

urlpatterns = [
    path("", views.create_objetivo, name="objetivos-create",),
    path("<int:pk>/", views.mix_objetivos, name="objetivos-mix"),
    path(
        "list/seguimiento/<int:pk>/",
        views.list_objetivos,
        name="objetivos-list",
    ),
    path("tipo/", views.create_tipo_objetivo, name="tipo-objetivo-create",),
    path("tipo/<int:pk>/", views.mix_tipo_objetivo, name="tipo-objetivo-mix"),
    path("tipo/list/", views.list_tipo_objetivo, name="tipo-objetivo-list"),
    path(
        "<int:objetivo_pk>/alumno/<int:pk>/",
        views.list_alumno_objetivo,
        name="alumno-objetivo-list",
    ),
    path(
        "alumno/<int:pk>/",
        views.get_alumno_objetivo,
        name="alumno-objetivo-get",
    ),
    path(
        "<int:pk>/alumno/",
        views.update_alumno_objetivo,
        name="alumno-objetivo-update",
    ),
]
