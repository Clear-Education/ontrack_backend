# from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings


schema_view = get_schema_view(
    openapi.Info(
        title="OnTrack API",
        default_version="v1",
        description="OnTrack",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="villegaswences@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("django-rq/", include("django_rq.urls")),
    path("api/users/", include("users.api.urls")),
    path("api/institucion/", include("instituciones.api.urls")),
    path("api/alumnos/", include("alumnos.api.urls")),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/", include("curricula.api.urls")),
    path("api/calificaciones/", include("calificaciones.api.urls")),
    path("api/asistencias/", include("asistencias.api.urls")),
    path("api/seguimientos/", include("seguimientos.api.urls")),
    path("api/objetivos/", include("objetivos.api.urls")),
    path("api/actualizaciones/", include("actualizaciones.api.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
