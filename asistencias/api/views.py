from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
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
from asistencias.api import serializers
from asistencias.models import Asistencia, AsistenciaAnioLectivo
from itertools import chain


class AsistenciaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("asistencia")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAsistenciaSerializer()}
    OK_LIST = {200: serializers.ViewAsistenciaSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        if (
            asistencia_retrieved.alumno_curso.alumno.institucion
            != request.user.institucion
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializers.ViewAsistenciaSerializer(asistencia_retrieved)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.UpdateAsistenciaSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        if (
            asistencia_retrieved.alumno_curso.alumno.institucion
            != request.user.institucion
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializers.UpdateAsistenciaSerializer(data=request.data)
        if serializer.is_valid():
            if not serializer.validated_data:
                return Response(
                    data={"detail": "Body vacío."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            asistencia_retrieved.asistio = serializer.validated_data.get(
                "asistio", asistencia_retrieved.asistio
            )
            asistencia_retrieved.descripcion = serializer.validated_data.get(
                "descripcion", asistencia_retrieved.descripcion
            )
            asistencia_retrieved.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        pass

    @swagger_auto_schema(
        request_body=serializers.CreateAsistenciaSerializer(),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.CreateAsistenciaSerializer(data=request.data)
        if serializer.is_valid():
            if (
                request.user.institucion
                != serializer.validated_data["alumno_curso"].alumno.institucion
            ):
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if serializer.validated_data["fecha"].weekday() >= 5:
                return Response(
                    data={
                        "detail": "No se pueden cargar asistencias para fines de semana"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not (
                serializer.validated_data[
                    "alumno_curso"
                ].anio_lectivo.fecha_desde
                < serializer.validated_data["fecha"]
                < serializer.validated_data[
                    "alumno_curso"
                ].anio_lectivo.fecha_hasta
            ):
                return Response(
                    data={
                        "detail": "La fecha especificada no se encuentra dentro del Año Lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            asistencias_existentes = Asistencia.objects.filter(
                fecha__exact=serializer.validated_data["fecha"],
                alumno_curso__id__exact=serializer.validated_data[
                    "alumno_curso"
                ].id,
            )
            if len(asistencias_existentes) != 0:
                return Response(
                    data={
                        "detail": "Ya existen una asistencia cargada para el alumno en el día especificado. Se debe modificar o borrar dicha asistencia"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            for value in serializer.errors.values():
                if value and any(
                    [
                        True if a.code == "does_not_exist" else False
                        for a in value
                    ]
                ):
                    return Response(
                        data={"detail": "No encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        request_body=serializers.CreateAsistenciaSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create_multiple(self, request):
        serializer = serializers.CreateAsistenciaSerializer(
            data=request.data, many=True
        )
        if serializer.is_valid():
            if len(serializer.validated_data) == 0:
                return Response(
                    data={"detail": "No se recibió ninguna información"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(
                set([a.get("alumno_curso") for a in serializer.validated_data])
            ) != len(serializer.validated_data):
                return Response(
                    data={
                        "detail": "No se pueden repetir alumnos en una misma llamada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                len(
                    set(
                        [
                            a.get("alumno_curso").curso.id
                            for a in serializer.validated_data
                        ]
                    )
                )
                != 1
            ):
                return Response(
                    data={
                        "detail": "No se pueden cargar asistencias para cursos distintos al mismo tiempo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                request.user.institucion
                != serializer.validated_data[0][
                    "alumno_curso"
                ].alumno.institucion
            ):
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if (
                len(set([a.get("fecha") for a in serializer.validated_data]))
                != 1
            ):
                return Response(
                    data={
                        "detail": "No se pueden cargar asistencias para distintas fechas al mismo tiempo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if serializer.validated_data[0]["fecha"].weekday() >= 5:
                return Response(
                    data={
                        "detail": "No se pueden cargar asistencias para fines de semana"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not (
                serializer.validated_data[0][
                    "alumno_curso"
                ].anio_lectivo.fecha_desde
                < serializer.validated_data[0]["fecha"]
                < serializer.validated_data[0][
                    "alumno_curso"
                ].anio_lectivo.fecha_hasta
            ):
                return Response(
                    data={
                        "detail": "La fecha especificada no se encuentra dentro del Año Lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            asistencias_existentes = Asistencia.objects.filter(
                fecha__exact=serializer.validated_data[0]["fecha"],
                alumno_curso__id__in=[
                    a.get("alumno_curso").id for a in serializer.validated_data
                ],
            )
            if len(asistencias_existentes) != 0:
                return Response(
                    data={
                        "detail": "Ya existen asistencias cargadas para algun alumno de los listados en el día especificado. Se debe modificar o borrar dicha asistencia"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            values = [a.values() for a in serializer.errors]
            for value in values:
                value = list(chain(*value))
                if value and any(
                    [
                        True if a.code == "does_not_exist" else False
                        for a in value
                    ]
                ):
                    return Response(
                        data={"detail": "No encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        request_body=serializers.ViewAsistenciaSerializer(),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def destroy_curso_dia(self, request):
        pass


create_asistencia = AsistenciaViewSet.as_view({"post": "create"})
mix_asistencia = AsistenciaViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
mix_asistencia_multiple = AsistenciaViewSet.as_view(
    {"post": "create_multiple", "delete": "destroy_curso_dia"}
)
list_asistencia = AsistenciaViewSet.as_view({"get": "list"})


class AsistenciaAnioLectivoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("asistenciaaniolectivo"),
    ]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.AsistenciaAnioLectivoSerializer(many=True)}
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
        request_body=serializers.AsistenciaAnioLectivoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass


hoy_asistencia_anio_lectivo = AsistenciaAnioLectivoViewSet.as_view(
    {"get": "get"}
)
