from django.urls import path
from instituciones.api import views
# from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', views.create_institucion, name='institucion-create'),
    path('<int:pk>/', views.update_institucion, name='institucion-view-update'),
    path('<int:pk>/status/', views.status_institucion, name='institucion-status'),
    path('list/', views.list_institucion, name='institucion-list'),
]