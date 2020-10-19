from rest_framework.viewsets import ModelViewSet
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses
from alumnos.models import Alumno, AlumnoCurso
from objetivos.api import serializers
from objetivos.models import Objetivo, TipoObjetivo, AlumnoObjetivo
from seguimientos.models import Seguimiento, IntegranteSeguimiento
import re
import datetime
import django_rq
from asistencias.rq_funcions import alumno_asistencia_redesign
from calificaciones.rq_funcions import alumno_calificacion_redesign

DATE_REGEX = r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"


class ObjetivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("objetivo")]
    pagination_class = None
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetObjetivoSerializer()}
    OK_LIST = {200: serializers.GetObjetivoSerializer(many=True)}
    OK_CREATED = {201: serializers.ReturnId()}
    OK_CREATED_MULTIPLE = {201: serializers.ReturnId(many=True)}

    @swagger_auto_schema(
        operation_id="get_objetivo",
        operation_description="""
        Obtener un objetivo utilizando su id.
        No se puede obtener un objetivo que no sea de la misma intitución o si no se pertenece al seguimiento.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        objetivo_retrieved = get_object_or_404(Objetivo, pk=pk)
        if (
            (
                objetivo_retrieved.seguimiento.institucion
                != request.user.institucion
            )
            or len(
                IntegranteSeguimiento.objects.filter(
                    seguimiento__exact=objetivo_retrieved.seguimiento,
                    usuario__exact=request.user,
                    fecha_hasta__isnull=True,
                )
            )
            == 0
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializers.GetObjetivoSerializer(objetivo_retrieved)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_objetivos",
        operation_description="""
        Se listan los objetivos de un seguimiento por su id.

        No se pueden listar objetivos de un seguimiento en el que no se es integrante
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, pk=None):
        seguimiento = get_object_or_404(Seguimiento, pk=pk)

        if (
            seguimiento.institucion != request.user.institucion
            or len(
                IntegranteSeguimiento.objects.filter(
                    seguimiento__id__exact=seguimiento.id,
                    usuario__exact=request.user,
                    fecha_hasta__isnull=True,
                )
            )
            == 0
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = Objetivo.objects.filter(seguimiento__id__exact=pk)

        serializer = serializers.GetObjetivoSerializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_objetivo",
        operation_description="""
        Modificación de un objetivo

        Solo es posible modificar el valor_objetivo_cuantitativo o la descripcion
        Solo puede hacerlo el encargado del seguimiento
        Si se modifica el valor_objetivo_cuantitativo, debe estar dentro de los límites establecidos
        en su tipo_objetivo (valor_minimo y valor_maximo)
        """,
        request_body=serializers.UpdateObjetivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        objetivo_retrieved = get_object_or_404(Objetivo, pk=pk)
        integrante = IntegranteSeguimiento.objects.filter(
            seguimiento__exact=objetivo_retrieved.seguimiento,
            usuario__exact=request.user,
            fecha_hasta__isnull=True,
        )
        if (
            objetivo_retrieved.seguimiento.institucion
            != request.user.institucion
        ) or len(integrante) == 0:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not objetivo_retrieved.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se puede modificar un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "encargado" not in integrante[0].rol.nombre.lower():
            return Response(
                data={"detail": "No tiene permiso para modificar el objetivo"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = serializers.UpdateObjetivoSerializer(
            objetivo_retrieved, data=request.data
        )
        if serializer.is_valid():
            tipo_objetivo = objetivo_retrieved.tipo_objetivo
            valor = serializer.validated_data.get(
                "valor_objetivo_cuantitativo"
            )
            descripcion = serializer.validated_data.get("descripcion")

            if not tipo_objetivo.cuantitativo:
                serializer.validated_data.pop(
                    "valor_objetivo_cuantitativo", None
                )
            else:
                if valor and not (
                    tipo_objetivo.valor_minimo
                    <= valor
                    <= tipo_objetivo.valor_maximo
                ):
                    return Response(
                        data={
                            "detail": f"No se encuentra en el rango permitido de {tipo_objetivo.valor_minimo} a {tipo_objetivo.valor_maximo}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer.save()

            if valor:
                objetivos_actualizar = (
                    AlumnoObjetivo.objects.filter(
                        objetivo__id__exact=objetivo_retrieved.id,
                        objetivo__tipo_objetivo__cuantitativo=True,
                    )
                    .order_by("alumno_curso", "-fecha_creacion")
                    .distinct("alumno_curso")
                )
                for objetivo_alumno in objetivos_actualizar:
                    if (
                        objetivo_alumno.valor >= valor
                        and not objetivo_alumno.alcanzada
                    ):
                        objetivo_alumno.alcanzada = True
                        objetivo_alumno.save()

            return Response(status=status.HTTP_200_OK)

        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="delete_objetivo",
        operation_description="""
        Borrado de un Objetivo con su id

        Solo puede borrar si es encargado y el seguimiento está en progreso.
        """,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        objetivo_retrieved = get_object_or_404(Objetivo, pk=pk)
        integrante = IntegranteSeguimiento.objects.filter(
            seguimiento__exact=objetivo_retrieved.seguimiento,
            usuario__exact=request.user,
            fecha_hasta__isnull=True,
        )

        if (
            objetivo_retrieved.seguimiento.institucion
            != request.user.institucion
        ) or len(integrante) == 0:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if "encargado" not in integrante[0].rol.nombre.lower():
            return Response(
                data={"detail": "No tiene permiso para borrar un objetivo"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not objetivo_retrieved.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se puede modificar un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        objetivo_retrieved.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_objetivo",
        operation_description="""
        Creación de un objetivo para un seguimiento (usando el id del seguimiento).

        No está permitido crear un objetivo si no es encargado del seguimiento.
        Si el tipo de objetivo no es multiple, no se puede crear más de un objetivo de ese tipo en el seguimiento.
        Si el tipo es cuantitativo, el valor_objetivo_cuantitativo es obligatorio y debe estar dentro del rango
        especificado en el tipo_objetivo (valor_minimo y valor_maximo)
        Si es cualitativo, la descripción es obligatoria
        """,
        request_body=serializers.CreateObjetivoSerializer(),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.CreateObjetivoSerializer(data=request.data)
        if serializer.is_valid():
            seguimiento = serializer.validated_data["seguimiento"]
            if seguimiento.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            integrante = IntegranteSeguimiento.objects.filter(
                seguimiento__exact=seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )

            if len(integrante) == 0:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if "encargado" not in integrante[0].rol.nombre.lower():
                return Response(
                    data={"detail": "No tiene permiso para crear un objetivo"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not seguimiento.en_progreso:
                return Response(
                    data={
                        "detail": "No se puede modificar un Seguimiento que no se encuentra en progreso"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tipo_objetivo = serializer.validated_data["tipo_objetivo"]
            valor = serializer.validated_data.get(
                "valor_objetivo_cuantitativo"
            )
            descripcion = serializer.validated_data.get("descripcion")

            if not tipo_objetivo.cuantitativo:
                if not descripcion:
                    return Response(
                        data={
                            "detail": "Para este tipo de objetivos es necesario fijar una descripción"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer.validated_data.pop(
                    "valor_objetivo_cuantitativo", None
                )
            else:
                if not valor or not (
                    tipo_objetivo.valor_minimo
                    <= valor
                    <= tipo_objetivo.valor_maximo
                ):
                    return Response(
                        data={
                            "detail": f"No se ingreso un valor, o no se encuentra en el rango permitido de {tipo_objetivo.valor_minimo} a {tipo_objetivo.valor_maximo}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not tipo_objetivo.multiple:
                existing_objetivo = Objetivo.objects.filter(
                    seguimiento__id__exact=seguimiento.id,
                    tipo_objetivo__id=tipo_objetivo.id,
                )
                if len(existing_objetivo) != 0:
                    return Response(
                        data={
                            "detail": "Ya existe un objetivo de este mismo tipo en el seguimiento. No está permitido tener dos objetivos del mismo tipo"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            new_objetivo = serializer.create(serializer.validated_data)
            return_serializer = serializers.ReturnId({"id": new_objetivo.id})
            if (
                new_objetivo.tipo_objetivo.cuantitativo
                and not new_objetivo.tipo_objetivo.multiple
                and re.search(
                    "Asistencia",
                    new_objetivo.tipo_objetivo.nombre,
                    flags=re.IGNORECASE,
                )
            ):
                for alumno_curso in new_objetivo.seguimiento.alumnos.all():
                    django_rq.enqueue(
                        alumno_asistencia_redesign,
                        alumno_curso.alumno.id,
                        datetime.datetime.now(),
                        new_objetivo.seguimiento.anio_lectivo.fecha_desde,
                    )
            elif (
                new_objetivo.tipo_objetivo.cuantitativo
                and not new_objetivo.tipo_objetivo.multiple
                and re.search(
                    "promedio",
                    new_objetivo.tipo_objetivo.nombre,
                    flags=re.IGNORECASE,
                )
            ):
                for alumno_curso in new_objetivo.seguimiento.alumnos.all():
                    materia = new_objetivo.seguimiento.materias.all()[0]
                    django_rq.enqueue(
                        alumno_calificacion_redesign,
                        alumno_curso.alumno.id,
                        materia.id,
                        new_objetivo.seguimiento.anio_lectivo.fecha_desde,
                    )

            return Response(
                data=return_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="create_multiple_objetivo",
        operation_description="""
        Creación de multiples objetivos para un seguimiento (usando el id del seguimiento).

        No está permitido crear un objetivo si no es encargado del seguimiento.
        Si el tipo de objetivo no es multiple, no se puede crear más de un objetivo de ese tipo en el seguimiento.
        Si el tipo es cuantitativo, el valor_objetivo_cuantitativo es obligatorio y debe estar dentro del rango
        especificado en el tipo_objetivo (valor_minimo y valor_maximo)
        Si es cualitativo, la descripción es obligatoria
        """,
        request_body=serializers.CreateMultipleObjetivoSerializer(),
        responses={**OK_CREATED_MULTIPLE, **responses.STANDARD_ERRORS},
    )
    def create_multiple(self, request):
        serializer = serializers.CreateMultipleObjetivoSerializer(
            data=request.data
        )
        if serializer.is_valid():
            seguimiento = serializer.validated_data["seguimiento"]
            if seguimiento.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            integrante = IntegranteSeguimiento.objects.filter(
                seguimiento__exact=seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )

            if len(integrante) == 0:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if "encargado" not in integrante[0].rol.nombre.lower():
                return Response(
                    data={"detail": "No tiene permiso para crear un objetivo"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not seguimiento.en_progreso:
                return Response(
                    data={
                        "detail": "No se puede modificar un Seguimiento que no se encuentra en progreso"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            objetivo_list = list()

            for objetivo in serializer.validated_data["objetivos"]:

                objetivo["seguimiento"] = seguimiento

                tipo_objetivo = objetivo["tipo_objetivo"]
                valor = objetivo.get("valor_objetivo_cuantitativo")
                descripcion = objetivo.get("descripcion")

                if not tipo_objetivo.cuantitativo:
                    if not descripcion:
                        return Response(
                            data={
                                "detail": "Para este tipo de objetivos es necesario fijar una descripción"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    objetivo.pop("valor_objetivo_cuantitativo", None)
                else:
                    if not valor or not (
                        tipo_objetivo.valor_minimo
                        <= valor
                        <= tipo_objetivo.valor_maximo
                    ):
                        return Response(
                            data={
                                "detail": f"No se ingreso un valor, o no se encuentra en el rango permitido de {tipo_objetivo.valor_minimo} a {tipo_objetivo.valor_maximo}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                if not tipo_objetivo.multiple:
                    existing_objetivo = Objetivo.objects.filter(
                        seguimiento__id__exact=seguimiento.id,
                        tipo_objetivo__id=tipo_objetivo.id,
                    )
                    if len(existing_objetivo) != 0:
                        return Response(
                            data={
                                "detail": "Ya existe un objetivo de este mismo tipo en el seguimiento. No está permitido tener dos objetivos del mismo tipo"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                objetivo = Objetivo(**objetivo)
                objetivo.save()
                objetivo_list.append(objetivo)

            if objetivo_list:
                for new_ob in objetivo_list:
                    if (
                        new_ob.tipo_objetivo.cuantitativo
                        and not new_ob.tipo_objetivo.multiple
                        and re.search(
                            "Asistencia",
                            new_ob.tipo_objetivo.nombre,
                            flags=re.IGNORECASE,
                        )
                    ):
                        for alumno_curso in new_ob.seguimiento.alumnos.all():
                            django_rq.enqueue(
                                alumno_asistencia_redesign,
                                alumno_curso.alumno.id,
                                datetime.datetime.now(),
                                new_ob.seguimiento.anio_lectivo.fecha_desde,
                            )
                    elif (
                        new_ob.tipo_objetivo.cuantitativo
                        and not new_ob.tipo_objetivo.multiple
                        and re.search(
                            "promedio",
                            new_ob.tipo_objetivo.nombre,
                            flags=re.IGNORECASE,
                        )
                    ):
                        for alumno_curso in new_ob.seguimiento.alumnos.all():
                            materia = new_ob.seguimiento.materias.all()[0]
                            django_rq.enqueue(
                                alumno_calificacion_redesign,
                                alumno_curso.alumno.id,
                                materia.id,
                                new_ob.seguimiento.anio_lectivo.fecha_desde,
                            )

                return_serializer = serializers.ReturnId(
                    [{"id": obj.id} for obj in objetivo_list], many=True,
                )
                return Response(
                    data=return_serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    data={"detail": "No hay objetivos para agregar"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_objetivo = ObjetivoViewSet.as_view({"post": "create"})
create_multiple_objetivo = ObjetivoViewSet.as_view({"post": "create_multiple"})
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
        Obtener Tipo de Objetivo
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        tipo_objetivo = get_object_or_404(TipoObjetivo, pk=pk)
        serializer = serializers.GetTipoObjetivoSerializer(
            tipo_objetivo, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_tipo_objetivos",
        operation_description="""
        Listar Tipos de Objetivos
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        queryset = TipoObjetivo.objects.all()
        serializer = serializers.GetTipoObjetivoSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


get_tipo_objetivo = TipoObjetivoViewSet.as_view({"get": "get"})
list_tipo_objetivo = TipoObjetivoViewSet.as_view({"get": "list"})


class AlumnoObjetivoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("alumnoobjetivo"),
    ]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetAlumnoObjetivoSerializer(many=False)}
    OK_LIST = {200: serializers.GetAlumnoObjetivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    seguimiento_parameter = openapi.Parameter(
        "seguimiento",
        openapi.IN_QUERY,
        description="Seguimiento por el que queremos filtrar la búsqueda",
        type=openapi.TYPE_INTEGER,
        required=False,
    )

    objetivo_parameter = openapi.Parameter(
        "objetivo",
        openapi.IN_QUERY,
        description="Objetivo por el que queremos filtrar la búsqueda",
        type=openapi.TYPE_INTEGER,
        required=False,
    )

    fecha_desde_parameter = openapi.Parameter(
        "fecha_desde",
        openapi.IN_QUERY,
        description="Fecha desde la cual queremos filtrar la búsqueda. En caso de no pasar una fecha_desde, fecha_hasta funciona como una fecha individual",
        type=openapi.TYPE_STRING,
        required=False,
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

    @swagger_auto_schema(
        operation_id="get_alumno_objetivo",
        manual_parameters=[objetivo_parameter, seguimiento_parameter],
        operation_description="""
        Obtener el último ObjetivoAlumno para un alumno.

        Sirve para obtener el último valor del ObjetivoAlumno para dicho alumno.

        Es necesario pasar como query param el seguimiento (id) o el objetivo (id).
        
        Si se pasa el seguimiento, se devuelve una lista con los últimos ObjetivoAlumno
        de dicho alumno para todos los objetivos existentes en el seguimiento.

        Si se pasa el objetivo, se devuelve solo el último ObjetivoAlumno para dicho 
        alumno en el objetivo especificado.

        Se debe ignorar los queryparams limit y offset
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):

        seguimiento = request.query_params.get("seguimiento")
        objetivo = request.query_params.get("objetivo")

        if seguimiento and objetivo:
            return Response(
                data={
                    "detail": "No se puede obtener por seguimiento y objetivo al mismo tiempo"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not seguimiento and not objetivo:
            return Response(
                data={"detail": "Es necesario pasar o seguimiento u objetivo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alumno_retrieved = get_object_or_404(Alumno, pk=pk)
        if alumno_retrieved.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        alumno_cursos = AlumnoCurso.objects.filter(
            alumno__exact=alumno_retrieved,
        )

        if seguimiento:
            if seguimiento.isnumeric():
                seguimiento = int(seguimiento)
            else:
                return Response(
                    data={"detail": "El valor de seguimiento no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seguimiento = get_object_or_404(Seguimiento, pk=seguimiento)
            if seguimiento.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            integrante = IntegranteSeguimiento.objects.filter(
                fecha_hasta__isnull=True,
                seguimiento__exact=seguimiento,
                usuario__exact=request.user,
            )
            if not integrante:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not any(
                [
                    a.id in map(lambda x: x.id, seguimiento.alumnos.all())
                    for a in alumno_cursos
                ]
            ):
                return Response(
                    data={"detail": "Alumno no pertenece a dicho seguimiento"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            objetivos = Objetivo.objects.filter(
                seguimiento__exact=seguimiento,
            )
            queryset = (
                AlumnoObjetivo.objects.filter(
                    objetivo__in=objetivos, alumno_curso__in=alumno_cursos,
                )
                .order_by("objetivo", "-fecha_creacion")
                .distinct("objetivo")
            )

            objetivos_filtered = filter(
                lambda x: not x.tipo_objetivo.cuantitativo, objetivos
            )
            queryset_filtered = [x.objetivo.id for x in queryset]
            alumno_curso = None
            for ac in alumno_cursos:
                if ac.anio_lectivo.id == seguimiento.anio_lectivo.id:
                    alumno_curso = ac
                    break

            for o in objetivos_filtered:
                if o.id not in queryset_filtered:
                    AlumnoObjetivo(
                        objetivo=o, alumno_curso=ac, alcanzada=False,
                    ).save()
            queryset = queryset.all()
            if not len(queryset):
                return Response(
                    data={
                        "detail": "El alumno no tiene hitos en dicho seguimiento"
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )

            serializer = serializers.GetAlumnoObjetivoSerializer(
                queryset, many=True
            )

        if objetivo:
            if objetivo.isnumeric():
                objetivo = int(objetivo)
            else:
                return Response(
                    data={"detail": "El valor de objetivo no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            objetivo = get_object_or_404(Objetivo, pk=objetivo)
            if objetivo.seguimiento.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            integrante = IntegranteSeguimiento.objects.filter(
                fecha_hasta__isnull=True,
                seguimiento__exact=objetivo.seguimiento,
                usuario__exact=request.user,
            )
            if not integrante:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not any(
                [
                    a.id
                    in map(lambda x: x.id, objetivo.seguimiento.alumnos.all())
                    for a in alumno_cursos
                ]
            ):
                return Response(
                    data={"detail": "Alumno no pertenece a dicho seguimiento"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = AlumnoObjetivo.objects.filter(
                objetivo__exact=objetivo, alumno_curso__in=alumno_cursos,
            ).order_by("-fecha_creacion")

            queryset_filtered = [x.objetivo.id for x in queryset]

            if (
                not objetivo.tipo_objetivo.cuantitativo
                and objetivo.id not in queryset_filtered
            ):

                alumno_curso = None
                for ac in alumno_cursos:
                    if (
                        ac.anio_lectivo.id
                        == objetivo.seguimiento.anio_lectivo.id
                    ):
                        alumno_curso = ac
                        break

                AlumnoObjetivo(
                    objetivo=objetivo, alumno_curso=ac, alcanzada=False,
                ).save()
            queryset = queryset.all()
            if not len(queryset):
                return Response(
                    data={
                        "detail": "El alumno no tiene hitos en dicho objetivo"
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )

            serializer = serializers.GetAlumnoObjetivoSerializer(queryset[0])

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_alumno_objetivos",
        manual_parameters=[fecha_desde_parameter, fecha_hasta_parameter],
        operation_description="""
        Obtener la lista de AlumnoObjetivos para un alumno especificado por su id (en la url) y
        un objetivo especificado por su id (en la url).

        Es útil para obtener la secuencia o progresion del alumno en dicho objetivo
        Como opcional se pueden pasar las fechas desde y fecha hasta (ninguna o ambas) para filtrar
        la búsqueda en dicho rango.
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, objetivo_pk=None, pk=None):
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")
        alumno_retrieved = get_object_or_404(Alumno, pk=pk)
        if alumno_retrieved.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        alumno_cursos = AlumnoCurso.objects.filter(
            alumno__exact=alumno_retrieved,
        )
        objetivo_retrieved = get_object_or_404(Objetivo, pk=objetivo_pk)
        if (
            objetivo_retrieved.seguimiento.institucion
            != request.user.institucion
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        integrante = IntegranteSeguimiento.objects.filter(
            fecha_hasta__isnull=True,
            seguimiento__exact=objetivo_retrieved.seguimiento,
            usuario__exact=request.user,
        )
        if not integrante:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not any(
            [
                a.id
                in map(
                    lambda x: x.id,
                    objetivo_retrieved.seguimiento.alumnos.all(),
                )
                for a in alumno_cursos
            ]
        ):
            return Response(
                data={"detail": "Alumno no pertenece a dicho seguimiento"},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = AlumnoObjetivo.objects.filter(
            objetivo__exact=objetivo_retrieved, alumno_curso__in=alumno_cursos,
        ).order_by("fecha_creacion")

        if fecha_desde:
            if not fecha_hasta:
                return Response(
                    data={
                        "detail": "Es necesario ingresar ambas fechas o ninguna"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
            queryset = queryset.filter(fecha_creacion__gte=fecha_desde)

        if fecha_hasta:
            if not fecha_desde:
                return Response(
                    data={
                        "detail": "Es necesario ingresar ambas fechas o ninguna"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
            queryset = queryset.filter(fecha_creacion__lte=fecha_hasta)

        if fecha_hasta and fecha_desde:
            if fecha_hasta <= fecha_desde:
                return Response(
                    data={"detail": "Las fechas ingresadas son inválidas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not len(queryset):
            return Response(
                data={"detail": "El alumno no tiene hitos en dicho objetivo"},
                status=status.HTTP_204_NO_CONTENT,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.GetAlumnoObjetivoSerializer(
                page, many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = serializers.GetAlumnoObjetivoSerializer(
            queryset, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_alumno_objetivo",
        operation_description="""
        Modificar el AlumnoObjetivo pasando el id del Objetivo.

        Solo se puede modificar el "alcanzada" de un AlumnoObjetivo que corresponda con un Objetivo
        de tipo cualitativo.
        Se puede pasar el id del alumno o del alumno_curso, pero no ambos al mismo tiempo.
        """,
        request_body=serializers.UpdateAlumnoObjetivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):

        objetivo_retrieved = get_object_or_404(Objetivo, pk=pk)
        if (
            objetivo_retrieved.seguimiento.institucion
            != request.user.institucion
        ):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if objetivo_retrieved.tipo_objetivo.cuantitativo:
            return Response(
                data={
                    "detail": "No se puede modificar el valor de un objetivo cuantitativo para un alumno."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        integrante = IntegranteSeguimiento.objects.filter(
            fecha_hasta__isnull=True,
            seguimiento__exact=objetivo_retrieved.seguimiento,
            usuario__exact=request.user,
        )
        if not integrante:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if "encargado" not in integrante[0].rol.nombre.lower():
            return Response(
                data={"detail": "No tiene permiso para modificar el objetivo"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = serializers.UpdateAlumnoObjetivoSerializer(
            data=request.data
        )
        if serializer.is_valid():
            alumno = serializer.validated_data.get("alumno")
            alumno_curso = serializer.validated_data.get("alumno_curso")

            if not alumno and not alumno_curso:
                return Response(
                    data={"detail": "Es necesario ingresar el Alumno"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if alumno and alumno_curso:
                return Response(
                    data={
                        "detail": "No se puede ingresar Alumno y AlumnoCurso al mismo tiempo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if alumno:
                if alumno.institucion != request.user.institucion:
                    return Response(
                        data={"detail": "No encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                alumno_cursos = AlumnoCurso.objects.filter(
                    alumno__exact=alumno,
                )
                if not any(
                    [
                        a.id
                        in map(
                            lambda x: x.id,
                            objetivo_retrieved.seguimiento.alumnos.all(),
                        )
                        for a in alumno_cursos
                    ]
                ):
                    return Response(
                        data={
                            "detail": "Alumno no pertenece a dicho seguimiento"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if not objetivo_retrieved.seguimiento.en_progreso:
                    return Response(
                        data={
                            "detail": "No se puede modificar un Seguimiento que no se encuentra en progreso"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                alumno_objetivo = AlumnoObjetivo.objects.get(
                    alumno_curso__in=alumno_cursos,
                    objetivo__exact=objetivo_retrieved,
                )

            if alumno_curso:
                if alumno_curso.alumno.institucion != request.user.institucion:
                    return Response(
                        data={"detail": "No encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if alumno_curso.id not in map(
                    lambda x: x.id,
                    objetivo_retrieved.seguimiento.alumnos.all(),
                ):
                    return Response(
                        data={
                            "detail": "Alumno no pertenece a dicho seguimiento"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                alumno_objetivo = AlumnoObjetivo.objects.get(
                    alumno_curso__exact=alumno_curso,
                    objetivo__exact=objetivo_retrieved,
                )

            if (
                alumno_objetivo.alcanzada
                == serializer.validated_data["alcanzada"]
            ):
                return Response(
                    data={
                        "detail": "El objetivo ya se encuentra en ese estado"
                    },
                    status=status.HTTP_200_OK,
                )

            alumno_objetivo.alcanzada = serializer.validated_data["alcanzada"]
            alumno_objetivo.save()

            return Response(
                data=serializers.GetAlumnoObjetivoSerializer(
                    alumno_objetivo
                ).data,
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


get_alumno_objetivo = AlumnoObjetivoViewSet.as_view({"get": "get"})
update_alumno_objetivo = AlumnoObjetivoViewSet.as_view({"patch": "update"})
list_alumno_objetivo = AlumnoObjetivoViewSet.as_view({"get": "list"})

