from django.urls import path
from seguimientos.api import views

# from rest_framework.routers import DefaultRouter


urlpatterns = [
    path("", views.create_seguimiento, name="seguimiento-create"),
    path(
        "<int:pk>/", views.view_edit_seguimiento, name="seguimiento-view-edit"
    ),
    path("list/", views.list_seguimiento, name="seguimiento-list"),
    # Rol
    path("rol/", views.create_rol, name="rolseguimiento-create"),
    path(
        "rol/<int:pk>/", views.view_edit_rol, name="rolseguimiento-view-edit"
    ),
    path("rol/list/", views.list_rol, name="rolseguimiento-list"),
]
