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
from alumnos.models import Alumno, AlumnoCurso
from django.core.validators import validate_integer
from asistencias.api import serializers
from asistencias.models import Asistencia
from itertools import chain
import re
import datetime
from django.db.models import Avg

DATE_REGEX = r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"


class AsistenciaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("asistencia")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAsistenciaSerializer()}
    OK_LIST = {200: serializers.ViewAsistenciaSerializer(many=True)}
    OK_CREATED = {201: ""}
    OK_VIEW_PORCENTAJE = {
        200: serializers.AsistenciaAnioLectivoSerializer(many=True)
    }

    alumno_curso_parameter = openapi.Parameter(
        "alumno_curso",
        openapi.IN_QUERY,
        description="Id del AlumnoCurso por el que queremos filtrar el listado. Sólo es requerido si no se pasa un curso",
        type=openapi.TYPE_INTEGER,
        required=True,
    )

    curso_parameter = openapi.Parameter(
        "curso",
        openapi.IN_QUERY,
        description="Id del Curso por el que queremos filtrar la búsqueda. Sólo es requerido si no se pasa un alumno_curso",
        type=openapi.TYPE_INTEGER,
        required=True,
    )

    fecha_desde_parameter = openapi.Parameter(
        "fecha_desde",
        openapi.IN_QUERY,
        description="Fecha desde la cual queremos filtrar la búsqueda. En caso de no pasar una fecha_desde, fecha_hasta funciona como una fecha individual",
        type=openapi.TYPE_STRING,
        required=True,
        pattern="DD-MM-YYYY",
    )

    fecha_hasta_parameter = openapi.Parameter(
        "fecha_hasta",
        openapi.IN_QUERY,
        description="Fecha hasta la cual queremos filtrar la búsqueda.",
        type=openapi.TYPE_STRING,
        required=False,
        pattern="DD-MM-YYYY",
    )

    alumno_curso_parameter_porcentaje = openapi.Parameter(
        "alumno_curso",
        openapi.IN_QUERY,
        description="Id del AlumnoCurso del cual queremos el porcentaje de asistencias",
        type=openapi.TYPE_INTEGER,
        required=True,
    )

    fecha_desde_parameter_porcentaje = openapi.Parameter(
        "fecha_desde",
        openapi.IN_QUERY,
        description="Fecha desde la cual queremos obtener el porcentaje de asistencias. Puede no pasarse ninguna fecha y se infiere el Año Lectivo completo",
        type=openapi.TYPE_STRING,
        required=True,
        pattern="DD-MM-YYYY",
    )

    fecha_hasta_parameter_porcentaje = openapi.Parameter(
        "fecha_hasta",
        openapi.IN_QUERY,
        description="Fecha hasta la cual queremos obtener el porcentaje de asistencias. Puede no pasarse ninguna fecha y se infiere el Año Lectivo completo",
        type=openapi.TYPE_STRING,
        required=True,
        pattern="DD-MM-YYYY",
    )

    @swagger_auto_schema(
        operation_id="get_asistencia",
        operation_description="""
        Obtener una asistencia utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
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

    @swagger_auto_schema(
        operation_id="list_asistencias",
        operation_description="""
        Listar asistencias de un alumno o un curso completo.
        Es necesario pasar el parametro de alumno_curso (id) o curso (id), pero no ambos al mismo tiempo.
        Es necesario también pasar la fecha_desde (si no se pasa fecha_hasta, actúa cómo fecha única).
        Es opcional pasar el parámetro fecha_hasta.
        """,
        manual_parameters=[
            alumno_curso_parameter,
            curso_parameter,
            fecha_desde_parameter,
            fecha_hasta_parameter,
        ],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        queryset = Asistencia.objects.filter(
            alumno_curso__alumno__institucion__exact=request.user.institucion
        )

        curso = request.query_params.get("curso", None)
        alumno_curso = request.query_params.get("alumno_curso", None)
        fecha_desde = request.query_params.get("fecha_desde", None)
        fecha_hasta = request.query_params.get("fecha_hasta", None)

        if fecha_desde:
            if not re.compile(DATE_REGEX).match(fecha_desde):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_desde.split("-")
            fecha_desde = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            if fecha_hasta:
                queryset = queryset.filter(fecha__gte=fecha_desde)
            else:
                queryset = queryset.filter(fecha__exact=fecha_desde)
        else:
            return Response(
                data={
                    "detail": "Es necesario ingresar al menos la fecha_desde"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fecha_hasta:
            if not re.compile(DATE_REGEX).match(fecha_hasta):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_hasta.split("-")
            fecha_hasta = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        if fecha_hasta and fecha_desde:
            if fecha_hasta <= fecha_desde:
                return Response(
                    data={"detail": "Las fechas ingresadas son inválidas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if curso and alumno_curso:
            return Response(
                data={
                    "detail": "No se puede listar por curso y por alumno_curso al mismo tiempo"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if curso:
            if curso.isnumeric():
                curso = int(curso)
            else:
                return Response(
                    data={"detail": "El valor de curso no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            curso = get_object_or_404(Curso, pk=curso)
            if curso.anio.carrera.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno_curso__curso__exact=curso)

        if alumno_curso:
            if alumno_curso.isnumeric():
                alumno_curso = int(alumno_curso)
            else:
                return Response(
                    data={"detail": "El valor de alumno_curso no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
            if alumno_curso.alumno.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno_curso__exact=alumno_curso)
        elif not curso:
            return Response(
                data={
                    "detail": "Es necesario ingresar un curso o alumno_curso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewAsistenciaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewAsistenciaSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_asistencia",
        operation_description="""
        Modificar una asistencia obtenida con su id.
        No es posible modificar el alumno o la fecha, sólo se puede modificar su valor de asistencia (asistió) y su descripción.
        """,
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

    @swagger_auto_schema(
        operation_id="delete_asistencia",
        operation_description="Borrado de una audiencia obtenida con el id",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        retrieved_asistencia = get_object_or_404(Asistencia, pk=pk)
        if (
            retrieved_asistencia.alumno_curso.alumno.institucion
            != request.user.institucion
        ):
            return Response(status=status.HTTP_404_NOT_FOUND,)
        retrieved_asistencia.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_asistencia",
        operation_description="""
        Creación de una asistencia.
        Es necesario ingresar la fecha, valor de la asistencia (asistio) e id del alumno_curso (alumno_curso).
        Se utiliza la entidad alumno curso porque permite situar al alumno en un curso en particular, durante un Año Lectivo particular.
        Se pueden pasar como dato opcional la descripción.
        """,
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
        operation_id="create_multiple_asistencias",
        operation_description="""
        Creación múltiple de asitencias.
        Los datos necesarios son los mismos que en la creación individual, sólo que obligatoriamente se debe pasar una lista de entidades.
        Como restricciones tiene:
        -  No se pueden repetir alumnos en la misma carga
        -  No se puede pasar una lista vacía
        -  No se pueden cargar asistencias de cursos distintos al mismo tiempo
        -  No se pueden cargar asistencias para distintas fechas al mismo tiempo
        -  No se pueden cargar asistencias para fines de semana
        -  No se pueden cargar asistencias para fechas fuera del rango del Año Lectivo
        -  No se puede cargar una asistencia si ya existe una asistencia para un alumno_curso de la lista. En este caso se debe borrar o modificar la asistencia a través de otros endpoints.
        """,
        request_body=serializers.CreateAsistenciaSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["POST"], name="create_multiple")
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
        operation_id="delete_multiple_asistencias",
        operation_description="""
        Borrado múltiple de asistencias.
        Como parámetro obligatorio es pasar alumno_curso o curso, pero no ambos al mismo tiempo, ya que el endpoint está diseñado para el borrado de
        todas las asistencias de un curso o de un alumno.
        Es necesario pasar por lo menos la fecha_desde, que actúa como fecha única si no se pasa fecha_hasta
        """,
        manual_parameters=[
            alumno_curso_parameter,
            curso_parameter,
            fecha_desde_parameter,
            fecha_hasta_parameter,
        ],
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["DELETE"], name="destroy_curso_dia")
    def destroy_curso_dia(self, request):
        queryset = Asistencia.objects.filter(
            alumno_curso__alumno__institucion__exact=request.user.institucion
        )

        curso = request.query_params.get("curso", None)
        alumno_curso = request.query_params.get("alumno_curso", None)
        fecha_desde = request.query_params.get("fecha_desde", None)
        fecha_hasta = request.query_params.get("fecha_hasta", None)

        if fecha_desde:
            if not re.compile(DATE_REGEX).match(fecha_desde):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_desde.split("-")
            fecha_desde = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            if fecha_hasta:
                queryset = queryset.filter(fecha__gte=fecha_desde)
            else:
                queryset = queryset.filter(fecha__exact=fecha_desde)
        else:
            return Response(
                data={
                    "detail": "Es necesario ingresar al menos la fecha_desde"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fecha_hasta:
            if not re.compile(DATE_REGEX).match(fecha_hasta):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_hasta.split("-")
            fecha_hasta = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        if fecha_hasta and fecha_desde:
            if fecha_hasta <= fecha_desde:
                return Response(
                    data={"detail": "Las fechas ingresadas son inválidas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if curso and alumno_curso:
            return Response(
                data={
                    "detail": "No se puede borrar por curso y por alumno_curso al mismo tiempo"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if curso:
            if curso.isnumeric():
                curso = int(curso)
            else:
                return Response(
                    data={"detail": "El valor de curso no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            curso = get_object_or_404(Curso, pk=curso)
            if curso.anio.carrera.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno_curso__curso__exact=curso)

        if alumno_curso:
            if alumno_curso.isnumeric():
                alumno_curso = int(alumno_curso)
            else:
                return Response(
                    data={"detail": "El valor de alumno_curso no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
            if alumno_curso.alumno.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno_curso__exact=alumno_curso)
        elif not curso:
            return Response(
                data={
                    "detail": "Es necesario ingresar un curso o alumno_curso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset.delete()

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="get_porcentaje_asistencias",
        operation_description="""
        Obtener el porcentaje de asistencias de un alumno en un determinado lapso de tiempo.
        Es necesario ingresar el alumno_curso, sobre el cual se obtiene el porcentaje calculado desde el inicio al fin del AnioLectivo.
        Se puede refinar el porcentaje pasando los parámetros fecha_desde y fecha_hasta (con valores dentro del AnioLectivo). En este
        caso, es necesario pasar ambas fechas, o ninguna.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        manual_parameters=[
            alumno_curso_parameter_porcentaje,
            fecha_desde_parameter_porcentaje,
            fecha_hasta_parameter_porcentaje,
        ],
        responses={**OK_VIEW_PORCENTAJE, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["GET"], name="porcentaje")
    def porcentaje(self, request, pk=None):
        queryset = Asistencia.objects.filter(
            alumno_curso__alumno__institucion__exact=request.user.institucion
        )

        alumno_curso = request.query_params.get("alumno_curso", None)
        fecha_desde = request.query_params.get("fecha_desde", None)
        fecha_hasta = request.query_params.get("fecha_hasta", None)

        if not alumno_curso:
            return Response(
                data={"detail": "Es necesario ingresar un alumno_curso"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            if alumno_curso.isnumeric():
                alumno_curso = int(alumno_curso)
            else:
                return Response(
                    data={"detail": "El valor de alumno_curso no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumno_curso = get_object_or_404(AlumnoCurso, pk=alumno_curso)
            if alumno_curso.alumno.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno_curso__exact=alumno_curso)

        if (fecha_desde and not fecha_hasta) or (
            fecha_hasta and not fecha_desde
        ):
            return Response(
                data={"detail": "Es necesario ingresar un rango de fechas"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fecha_desde:
            if not re.compile(DATE_REGEX).match(fecha_desde):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_desde.split("-")
            fecha_desde = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            fecha_desde_anio = alumno_curso.anio_lectivo.fecha_desde
            fecha_hasta_anio = alumno_curso.anio_lectivo.fecha_hasta

            if not (fecha_desde_anio <= fecha_desde <= fecha_hasta_anio):
                return Response(
                    data={
                        "detail": "La fecha_desde no se encuentra en el rango del AnioLectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(fecha__gte=fecha_desde)

        if fecha_hasta:
            if not re.compile(DATE_REGEX).match(fecha_hasta):
                return Response(
                    data={
                        "detail": "La fecha ingresada no está correctamente expresada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            temp = fecha_hasta.split("-")
            fecha_hasta = datetime.date(
                int(temp[2]), int(temp[1]), int(temp[0])
            )
            fecha_desde_anio = alumno_curso.anio_lectivo.fecha_desde
            fecha_hasta_anio = alumno_curso.anio_lectivo.fecha_hasta

            if not (fecha_desde_anio <= fecha_hasta <= fecha_hasta_anio):
                return Response(
                    data={
                        "detail": "La fecha_hasta no se encuentra en el rango del AnioLectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(fecha__lte=fecha_hasta)

            if fecha_hasta <= fecha_desde:
                return Response(
                    data={"detail": "Las fechas ingresadas son inválidas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        porcentaje = queryset.aggregate(Avg("asistio"))["asistio__avg"]

        data = {
            "porcentaje": porcentaje if porcentaje else 0.0,
            "alumno_curso": alumno_curso,
            "fecha_desde": fecha_desde if fecha_desde else None,
            "fecha_hasta": fecha_hasta if fecha_hasta else None,
        }

        serializer = serializers.AsistenciaAnioLectivoSerializer(
            data, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)


create_asistencia = AsistenciaViewSet.as_view({"post": "create"})
mix_asistencia = AsistenciaViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
mix_asistencia_multiple = AsistenciaViewSet.as_view(
    {"post": "create_multiple", "delete": "destroy_curso_dia"}
)
list_asistencia = AsistenciaViewSet.as_view({"get": "list"})
hoy_asistencia_anio_lectivo = AsistenciaViewSet.as_view({"get": "porcentaje"})

