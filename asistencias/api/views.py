from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from alumnos.api import serializers
from curricula.models import Curso, AnioLectivo
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses
from users.models import User
from alumnos.models import Alumno
from django.core.validators import validate_integer


class AsistenciaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("asistencia")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAlumnoSerializer()}
    OK_LIST = {200: serializers.ViewAlumnoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        pass

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.UpdateAlumnoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAlumnoSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAlumnoSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create_multiple(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAlumnoSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def destroy_curso_dia(self, request):
        pass


create_delete_curso_asistencia = AsistenciaViewSet.as_view(
    {"post": "create", "delete": "destroy_curso_dia"}
)
mix_asistencia = AsistenciaViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
create_asistencia_multiple = AsistenciaViewSet.as_view(
    {"post": "create_multiple"}
)
list_asistencia = AsistenciaViewSet.as_view({"get": "list"})


class AsistenciaAnioLectivoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("asistenciaaniolectivo"),
    ]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAlumnoCursoSerializer()}
    OK_LIST = {200: serializers.ViewAlumnoCursoSerializer(many=True)}
    OK_CREATED = {201: ""}

    anio_lectivo_parameter = openapi.Parameter(
        "anio_lectivo",
        openapi.IN_QUERY,
        description="Anio lectivo por el que queremos filtrar la búsqueda",
        type=openapi.TYPE_INTEGER,
    )

    curso_parameter = openapi.Parameter(
        "curso",
        openapi.IN_QUERY,
        description="Curso por el que queremos filtrar la búsqueda",
        type=openapi.TYPE_INTEGER,
    )

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS})
    def get(self, request, pk=None):
        pass

    @swagger_auto_schema(
        manual_parameters=[anio_lectivo_parameter, curso_parameter],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAlumnoCursoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass


list_asistencia_anio_lectivo = AsistenciaAnioLectivoViewSet.as_view(
    {"get": "list"}
)
hoy_asistencia_anio_lectivo = AsistenciaAnioLectivoViewSet.as_view(
    {"get": "get"}
)
