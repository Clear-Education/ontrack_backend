from django.urls import path
from instituciones.api import views
# from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', views.create_institucion, name='create'),
    path('<int:pk>/', views.update_institucion, name='viwe_update'),
    path('<int:pk>/alta/', views.alta_institucion, name='alta'),
    path('list/', views.list_institucion, name='list'),
]