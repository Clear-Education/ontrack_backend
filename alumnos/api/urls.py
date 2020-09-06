from alumnos.api import views
from django.urls import path

urlpatterns = [
    path("", views.create_alumno, name="alumno-create"),
    path("list/", views.list_alumno, name="alumno-list"),
    path("<int:pk>/", views.mix_alumno, name="mix-alumno"),
    path("curso/", views.create_alumno_curso, name="alumnocurso-create"),
    path(
        "curso/multiple/",
        views.multiple_alumno_curso,
        name="alumnocurso-create-multiple",
    ),
    path("curso/list/", views.list_alumno_curso, name="alumnocurso-list"),
    path("curso/<int:pk>/", views.mix_alumno_curso, name="alumnocurso-mix"),
]
