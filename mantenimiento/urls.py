from django.urls import path
from mantenimiento import views


urlpatterns = [
    path("", views.backup, name="backups"),
]
