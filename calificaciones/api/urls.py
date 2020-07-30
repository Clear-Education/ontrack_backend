from django.urls import path
from calificaciones.api import views

urlpatterns = [
    # Carrera
    path("", views.create_calificaciones, name="calificaciones-create",),
    path(
        "multiple/",
        views.create_calificaciones_multiple,
        name="calificaciones-create-multiple",
    ),
]
