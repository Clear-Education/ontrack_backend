from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from users.api.views import (
    register, logout, group_get, group_list, list_users)
# from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('logout/', logout, name="logout"),
    path('password-reset/', include(
        'django_rest_passwordreset.urls', namespace='password_reset')),
    path('groups/<int:pk>/', group_get, name='view_group'),
    path('groups/list/', group_list, name='list_group'),
    path('list/', list_users, name="user_list"),
]