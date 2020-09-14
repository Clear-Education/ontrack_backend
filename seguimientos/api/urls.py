from django.urls import path
from seguimientos.api import views

# from rest_framework.routers import DefaultRouter


urlpatterns = [
    # Seguimiento
    path("", views.create_seguimiento, name="seguimiento-create"),
    path(
        "<int:pk>/", views.view_edit_seguimiento, name="seguimiento-view-edit"
    ),
    path(
        "<int:pk>/status/", views.status_seguimiento, name="seguimiento-status"
    ),
    path("list/", views.list_seguimiento, name="seguimiento-list"),
    # Integrantes
    path(
        "<int:seguimiento>/integrantes/list/",
        views.list_integrantes,
        name="integrantes-list",
    ),
    path(
        "<int:seguimiento>/integrantes/",
        views.edit_integrantes,
        name="integrantes-edit",
    ),
    path(
        "<int:seguimiento>/integrantes/<int:pk>/",
        views.view_delete_integrantes,
        name="integrantes-view-delete",
    ),
    # Rol
    path("rol/", views.create_rol, name="rolseguimiento-create"),
    path(
        "rol/<int:pk>/", views.view_edit_rol, name="rolseguimiento-view-edit"
    ),
    path("rol/list/", views.list_rol, name="rolseguimiento-list"),
    # Solicitudes de Seguimiento
    path(
        "solicitudes/list/", views.list_solicitudes, name="solicitudes-list",
    ),
    path(
        "solicitudes/<int:pk>/",
        views.view_edit_delete_solicitudes,
        name="solicitudes-view-edit",
    ),
    path(
        "solicitudes/<int:pk>/status/",
        views.status_solicitud,
        name="solicitudes-status",
    ),
    path("solicitudes/", views.create_solicitudes, name="solicitudes-create"),
]
