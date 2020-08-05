from django.urls import path
from calificaciones.api import views

urlpatterns = [
    path("", views.create_calificaciones, name="calificaciones-create",),
    path(
        "multiple/",
        views.create_calificaciones_multiple,
        name="calificaciones-create-delete-multiple",
    ),
    path(
        "<int:pk>/",
        views.view_edit_calificacion,
        name="calificaciones-view_edit",
    ),
    path("list/", views.list_calificaciones, name="calificaciones-list",),
    path(
        "stats/promedio/",
        views.promedio_calificaciones,
        name="calificaciones-promedio",
    ),
]
