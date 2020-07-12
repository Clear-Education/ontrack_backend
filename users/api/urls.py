from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from users.api.views import (
    register,
    logout,
    group_get,
    group_list,
    list_users,
    login,
    change_password,
    update_user,
    revive_user,
)

# from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name="logout"),
    path('change_password/', change_password, name='change_password'),
    path('password-reset/', include(
        'django_rest_passwordreset.urls', namespace='password_reset')),
    path('groups/<int:pk>/', group_get, name='view_group'),
    path('groups/list/', group_list, name='list_group'),
    path('list/', list_users, name="user_list"),
    path('<int:pk>/', update_user, name="update_user"),
    path('<int:pk>/alta/', revive_user, name="revive_user"),
]
