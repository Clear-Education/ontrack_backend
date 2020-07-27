from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from alumnos.api import serializers
from curricula.models import Carrera, Anio, Curso, AnioLectivo
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from users.models import User


class AlumnoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumno")]
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
        request_body=serializers.CreateAlumnoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass


create_alumno = AlumnoViewSet.as_view({"post": "create"})
list_alumno = AlumnoViewSet.as_view({"get": "list"})
mix_alumno = AlumnoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)


class AlumnoCursoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumno")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAlumnoCursoSerializer()}
    OK_LIST = {200: serializers.ViewAlumnoCursoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        pass

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        pass

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAlumnoCursoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass


create_alumno_curso = AlumnoCursoViewSet.as_view({"post": "create"})
list_alumno_curso = AlumnoCursoViewSet.as_view({"get": "list"})
mix_alumno_curso = AlumnoCursoViewSet.as_view(
    {"get": "get", "delete": "destroy"}
)
