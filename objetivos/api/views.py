from rest_framework.viewsets import ModelViewSet

# from rest_framework.decorators import action
# from curricula.models import Curso, AnioLectivo
# from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses

# from users.models import User
# from alumnos.models import Alumno, AlumnoCurso
# from django.core.validators import validate_integer
from objetivos.api import serializers
from objetivos.models import Objetivo, TipoObjetivo, AlumnoObjetivo

# from itertools import chain
# import re
import datetime

# from django.db.models import Avg

DATE_REGEX = r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"


class ObjetivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("objetivo")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetObjetivoSerializer()}
    OK_LIST = {200: serializers.GetObjetivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="get_objetivo",
        operation_description="""
        Obtener un objetivo utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.ViewAsistenciaSerializer(asistencia_retrieved)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_objetivos",
        operation_description="""
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        pass
        # queryset = Asistencia.objects.filter(
        #     alumno_curso__alumno__institucion__exact=request.user.institucion
        # )

        # curso = request.query_params.get("curso", None)
        # alumno_curso = request.query_params.get("alumno_curso", None)
        # fecha_desde = request.query_params.get("fecha_desde", None)
        # fecha_hasta = request.query_params.get("fecha_hasta", None)

        # if fecha_desde:
        #     if not re.compile(DATE_REGEX).match(fecha_desde):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_desde.split("-")
        #     fecha_desde = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     if fecha_hasta:
        #         queryset = queryset.filter(fecha__gte=fecha_desde)
        #     else:
        #         queryset = queryset.filter(fecha__exact=fecha_desde)
        # else:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar al menos la fecha_desde"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if fecha_hasta:
        #     if not re.compile(DATE_REGEX).match(fecha_hasta):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_hasta.split("-")
        #     fecha_hasta = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     queryset = queryset.filter(fecha__lte=fecha_hasta)

        # if fecha_hasta and fecha_desde:
        #     if fecha_hasta <= fecha_desde:
        #         return Response(
        #             data={"detail": "Las fechas ingresadas son inválidas"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )

        # if curso and alumno_curso:
        #     return Response(
        #         data={
        #             "detail": "No se puede listar por curso y por alumno_curso al mismo tiempo"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if curso:
        #     if curso.isnumeric():
        #         curso = int(curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     curso = get_object_or_404(Curso, pk=curso)
        #     if curso.anio.carrera.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__curso__exact=curso)

        # if alumno_curso:
        #     if alumno_curso.isnumeric():
        #         alumno_curso = int(alumno_curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de alumno_curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
        #     if alumno_curso.alumno.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__exact=alumno_curso)
        # elif not curso:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar un curso o alumno_curso"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = serializers.ViewAsistenciaSerializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = serializers.ViewAsistenciaSerializer(queryset, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_objetivo",
        operation_description="""
        """,
        request_body=serializers.UpdateObjetivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.UpdateAsistenciaSerializer(data=request.data)
        # if serializer.is_valid():
        #     if not serializer.validated_data:
        #         return Response(
        #             data={"detail": "Body vacío."},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     asistencia_retrieved.asistio = serializer.validated_data.get(
        #         "asistio", asistencia_retrieved.asistio
        #     )
        #     asistencia_retrieved.descripcion = serializer.validated_data.get(
        #         "descripcion", asistencia_retrieved.descripcion
        #     )
        #     asistencia_retrieved.save()
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )

    @swagger_auto_schema(
        operation_id="delete_objetivo",
        operation_description="Borrado de un Objetivo con su id",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        pass
        # retrieved_asistencia = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     retrieved_asistencia.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(status=status.HTTP_404_NOT_FOUND,)
        # retrieved_asistencia.delete()
        # return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_objetivo",
        operation_description="""
        """,
        request_body=serializers.CreateObjetivoSerializer(),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass
        # serializer = serializers.CreateAsistenciaSerializer(data=request.data)
        # if serializer.is_valid():
        #     if (
        #         request.user.institucion
        #         != serializer.validated_data["alumno_curso"].alumno.institucion
        #     ):
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     if serializer.validated_data["fecha"].weekday() >= 5:
        #         return Response(
        #             data={
        #                 "detail": "No se pueden cargar asistencias para fines de semana"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     if not (
        #         serializer.validated_data[
        #             "alumno_curso"
        #         ].anio_lectivo.fecha_desde
        #         < serializer.validated_data["fecha"]
        #         < serializer.validated_data[
        #             "alumno_curso"
        #         ].anio_lectivo.fecha_hasta
        #     ):
        #         return Response(
        #             data={
        #                 "detail": "La fecha especificada no se encuentra dentro del Año Lectivo"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     asistencias_existentes = Asistencia.objects.filter(
        #         fecha__exact=serializer.validated_data["fecha"],
        #         alumno_curso__id__exact=serializer.validated_data[
        #             "alumno_curso"
        #         ].id,
        #     )
        #     if len(asistencias_existentes) != 0:
        #         return Response(
        #             data={
        #                 "detail": "Ya existen una asistencia cargada para el alumno en el día especificado. Se debe modificar o borrar dicha asistencia"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     serializer.save()
        #     return Response(status=status.HTTP_201_CREATED)
        # else:
        #     for value in serializer.errors.values():
        #         if value and any(
        #             [
        #                 True if a.code == "does_not_exist" else False
        #                 for a in value
        #             ]
        #         ):
        #             return Response(
        #                 data={"detail": "No encontrado."},
        #                 status=status.HTTP_404_NOT_FOUND,
        #             )

        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )


create_objetivo = ObjetivoViewSet.as_view({"post": "create"})
mix_objetivos = ObjetivoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
list_objetivos = ObjetivoViewSet.as_view({"get": "list"})


class TipoObjetivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("tipoobjetivo")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetTipoObjetivoSerializer()}
    OK_LIST = {200: serializers.GetTipoObjetivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="get_tipo_objetivo",
        operation_description="""
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.ViewAsistenciaSerializer(asistencia_retrieved)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_tipo_objetivos",
        operation_description="""
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        pass
        # queryset = Asistencia.objects.filter(
        #     alumno_curso__alumno__institucion__exact=request.user.institucion
        # )

        # curso = request.query_params.get("curso", None)
        # alumno_curso = request.query_params.get("alumno_curso", None)
        # fecha_desde = request.query_params.get("fecha_desde", None)
        # fecha_hasta = request.query_params.get("fecha_hasta", None)

        # if fecha_desde:
        #     if not re.compile(DATE_REGEX).match(fecha_desde):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_desde.split("-")
        #     fecha_desde = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     if fecha_hasta:
        #         queryset = queryset.filter(fecha__gte=fecha_desde)
        #     else:
        #         queryset = queryset.filter(fecha__exact=fecha_desde)
        # else:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar al menos la fecha_desde"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if fecha_hasta:
        #     if not re.compile(DATE_REGEX).match(fecha_hasta):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_hasta.split("-")
        #     fecha_hasta = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     queryset = queryset.filter(fecha__lte=fecha_hasta)

        # if fecha_hasta and fecha_desde:
        #     if fecha_hasta <= fecha_desde:
        #         return Response(
        #             data={"detail": "Las fechas ingresadas son inválidas"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )

        # if curso and alumno_curso:
        #     return Response(
        #         data={
        #             "detail": "No se puede listar por curso y por alumno_curso al mismo tiempo"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if curso:
        #     if curso.isnumeric():
        #         curso = int(curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     curso = get_object_or_404(Curso, pk=curso)
        #     if curso.anio.carrera.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__curso__exact=curso)

        # if alumno_curso:
        #     if alumno_curso.isnumeric():
        #         alumno_curso = int(alumno_curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de alumno_curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
        #     if alumno_curso.alumno.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__exact=alumno_curso)
        # elif not curso:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar un curso o alumno_curso"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = serializers.ViewAsistenciaSerializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = serializers.ViewAsistenciaSerializer(queryset, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_tipo_objetivo",
        operation_description="""
        """,
        request_body=serializers.UpdateTipoObjetivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.UpdateAsistenciaSerializer(data=request.data)
        # if serializer.is_valid():
        #     if not serializer.validated_data:
        #         return Response(
        #             data={"detail": "Body vacío."},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     asistencia_retrieved.asistio = serializer.validated_data.get(
        #         "asistio", asistencia_retrieved.asistio
        #     )
        #     asistencia_retrieved.descripcion = serializer.validated_data.get(
        #         "descripcion", asistencia_retrieved.descripcion
        #     )
        #     asistencia_retrieved.save()
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )

    @swagger_auto_schema(
        operation_id="delete_tipo_objetivo",
        operation_description="Borrado de un TipoObjetivo con su id",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        pass
        # retrieved_asistencia = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     retrieved_asistencia.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(status=status.HTTP_404_NOT_FOUND,)
        # retrieved_asistencia.delete()
        # return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_tipo_objetivo",
        operation_description="""
        """,
        request_body=serializers.CreateTipoObjetivoSerializer(),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass
        # serializer = serializers.CreateAsistenciaSerializer(data=request.data)
        # if serializer.is_valid():
        #     if (
        #         request.user.institucion
        #         != serializer.validated_data["alumno_curso"].alumno.institucion
        #     ):
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     if serializer.validated_data["fecha"].weekday() >= 5:
        #         return Response(
        #             data={
        #                 "detail": "No se pueden cargar asistencias para fines de semana"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     if not (
        #         serializer.validated_data[
        #             "alumno_curso"
        #         ].anio_lectivo.fecha_desde
        #         < serializer.validated_data["fecha"]
        #         < serializer.validated_data[
        #             "alumno_curso"
        #         ].anio_lectivo.fecha_hasta
        #     ):
        #         return Response(
        #             data={
        #                 "detail": "La fecha especificada no se encuentra dentro del Año Lectivo"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     asistencias_existentes = Asistencia.objects.filter(
        #         fecha__exact=serializer.validated_data["fecha"],
        #         alumno_curso__id__exact=serializer.validated_data[
        #             "alumno_curso"
        #         ].id,
        #     )
        #     if len(asistencias_existentes) != 0:
        #         return Response(
        #             data={
        #                 "detail": "Ya existen una asistencia cargada para el alumno en el día especificado. Se debe modificar o borrar dicha asistencia"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     serializer.save()
        #     return Response(status=status.HTTP_201_CREATED)
        # else:
        #     for value in serializer.errors.values():
        #         if value and any(
        #             [
        #                 True if a.code == "does_not_exist" else False
        #                 for a in value
        #             ]
        #         ):
        #             return Response(
        #                 data={"detail": "No encontrado."},
        #                 status=status.HTTP_404_NOT_FOUND,
        #             )

        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )


create_tipo_objetivo = TipoObjetivoViewSet.as_view({"post": "create"})
mix_tipo_objetivo = TipoObjetivoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
list_tipo_objetivo = TipoObjetivoViewSet.as_view({"get": "list"})


class AlumnoObjetivoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("alumnoobjetivo"),
    ]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetAlumnoObjetivoSerializer()}
    OK_LIST = {200: serializers.GetAlumnoObjetivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="get_alumno_objetivo",
        operation_description="""
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.ViewAsistenciaSerializer(asistencia_retrieved)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_alumno_objetivos",
        operation_description="""
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        pass
        # queryset = Asistencia.objects.filter(
        #     alumno_curso__alumno__institucion__exact=request.user.institucion
        # )

        # curso = request.query_params.get("curso", None)
        # alumno_curso = request.query_params.get("alumno_curso", None)
        # fecha_desde = request.query_params.get("fecha_desde", None)
        # fecha_hasta = request.query_params.get("fecha_hasta", None)

        # if fecha_desde:
        #     if not re.compile(DATE_REGEX).match(fecha_desde):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_desde.split("-")
        #     fecha_desde = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     if fecha_hasta:
        #         queryset = queryset.filter(fecha__gte=fecha_desde)
        #     else:
        #         queryset = queryset.filter(fecha__exact=fecha_desde)
        # else:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar al menos la fecha_desde"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if fecha_hasta:
        #     if not re.compile(DATE_REGEX).match(fecha_hasta):
        #         return Response(
        #             data={
        #                 "detail": "La fecha ingresada no está correctamente expresada"
        #             },
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     temp = fecha_hasta.split("-")
        #     fecha_hasta = datetime.date(
        #         int(temp[2]), int(temp[1]), int(temp[0])
        #     )
        #     queryset = queryset.filter(fecha__lte=fecha_hasta)

        # if fecha_hasta and fecha_desde:
        #     if fecha_hasta <= fecha_desde:
        #         return Response(
        #             data={"detail": "Las fechas ingresadas son inválidas"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )

        # if curso and alumno_curso:
        #     return Response(
        #         data={
        #             "detail": "No se puede listar por curso y por alumno_curso al mismo tiempo"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if curso:
        #     if curso.isnumeric():
        #         curso = int(curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     curso = get_object_or_404(Curso, pk=curso)
        #     if curso.anio.carrera.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__curso__exact=curso)

        # if alumno_curso:
        #     if alumno_curso.isnumeric():
        #         alumno_curso = int(alumno_curso)
        #     else:
        #         return Response(
        #             data={"detail": "El valor de alumno_curso no es numérico"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
        #     if alumno_curso.alumno.institucion != request.user.institucion:
        #         return Response(
        #             data={"detail": "No encontrado."},
        #             status=status.HTTP_404_NOT_FOUND,
        #         )
        #     queryset = queryset.filter(alumno_curso__exact=alumno_curso)
        # elif not curso:
        #     return Response(
        #         data={
        #             "detail": "Es necesario ingresar un curso o alumno_curso"
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = serializers.ViewAsistenciaSerializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = serializers.ViewAsistenciaSerializer(queryset, many=True)
        # return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_alumno_objetivo",
        operation_description="""
        """,
        request_body=serializers.UpdateAlumnoObjetivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass
        # asistencia_retrieved = get_object_or_404(Asistencia, pk=pk)
        # if (
        #     asistencia_retrieved.alumno_curso.alumno.institucion
        #     != request.user.institucion
        # ):
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # serializer = serializers.UpdateAsistenciaSerializer(data=request.data)
        # if serializer.is_valid():
        #     if not serializer.validated_data:
        #         return Response(
        #             data={"detail": "Body vacío."},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     asistencia_retrieved.asistio = serializer.validated_data.get(
        #         "asistio", asistencia_retrieved.asistio
        #     )
        #     asistencia_retrieved.descripcion = serializer.validated_data.get(
        #         "descripcion", asistencia_retrieved.descripcion
        #     )
        #     asistencia_retrieved.save()
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )


mix_alumno_objetivo = AlumnoObjetivoViewSet.as_view(
    {"get": "get", "patch": "update"}
)
list_alumno_objetivo = AlumnoObjetivoViewSet.as_view({"get": "list"})

