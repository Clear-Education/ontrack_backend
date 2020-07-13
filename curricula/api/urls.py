from curricula.api import views
from django.urls import include, path

urlpatterns = [
    path("carrera/", views.create_carrera, name="carrera-create"),
    path(
        "carrera/<int:pk>/", views.view_edit_carrera, name="carrera-view-edit"
    ),
    path("carrera/list/", views.list_carrera, name="carrera-list"),
]
