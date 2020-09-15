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
from drf_yasg import openapi
from ontrack import responses
from users.models import User
from alumnos.models import Alumno, AlumnoCurso
from django.core.validators import validate_integer
from itertools import chain
from django.core.exceptions import ValidationError
import datetime


class AlumnoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumno")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAlumnoSerializer()}
    OK_LIST = {200: serializers.ViewAlumnoSerializer(many=True)}
    OK_CREATED = {201: ""}

    anio_lectivo_parameter = openapi.Parameter(
        "anio_lectivo",
        openapi.IN_QUERY,
        description="Anio lectivo por el que queremos filtrar la búsqueda. Alumnos que no tienen curso en dicho año lectivo",
        type=openapi.TYPE_INTEGER,
    )

    @swagger_auto_schema(
        operation_id="get_alumno",
        operation_description="""
        Obtener un Alumno utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        alumno = get_object_or_404(Alumno, pk=pk)
        if alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAlumnoSerializer(alumno, many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_alumnos",
        operation_description="""
        Listar los alumnos de la institucion.

        Es posible pasar un query_param "anio_lectivo", el cual devolverá los alumnos que no estén asignados
        a un curso para dicho Año Lectivo.
        """,
        manual_parameters=[anio_lectivo_parameter],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        queryset = Alumno.objects.filter(
            institucion__exact=request.user.institucion
        )

        anio_lectivo = request.query_params.get("anio_lectivo", None)

        if anio_lectivo:
            if anio_lectivo.isnumeric():
                anio_lectivo = int(anio_lectivo)
            else:
                return Response(
                    data={"detail": "El valor de Año Lectivo no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            anio_lectivo_retrieved = get_object_or_404(
                AnioLectivo, pk=anio_lectivo
            )

            if anio_lectivo_retrieved.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            alumno_curso_list = AlumnoCurso.objects.filter(
                anio_lectivo__pk__exact=anio_lectivo,
            )
            queryset = queryset.exclude(
                id__in=[ac.alumno.id for ac in alumno_curso_list]
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewAlumnoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewAlumnoSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_alumno",
        operation_description="""
        Modificar un Alumno utilizando su id.
        Se pueden modificar los siguientes campos:
        -  dni (debe estar disponible)
        -  nombre
        -  apellido
        -  email
        -  legajo
        -  fecha_nacimiento
        -  direccion
        -  localidad
        -  provincia
        -  fecha_inscripcion
        """,
        request_body=serializers.UpdateAlumnoSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        institucion = request.user.institucion

        if retrieved_alumno.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = serializers.UpdateAlumnoSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data.get("dni"):
                if retrieved_alumno.dni != serializer.validated_data.get(
                    "dni"
                ):
                    try:
                        Alumno.objects.get(
                            dni=serializer.validated_data.get("dni")
                        )
                        return Response(
                            data={
                                "detail": "Alumno con el mismo dni existente"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    except Alumno.DoesNotExist:
                        pass
                    except:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                serializer.update(retrieved_alumno)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="delete_alumno",
        operation_description="Borrar un Alumno utilizando su id.",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        if retrieved_alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND,)
        hoy = datetime.date.today()
        anio_corriente = AnioLectivo.objects.filter(
            fecha_hasta__gte=hoy, fecha_desde__lte=hoy
        ).first()
        if anio_corriente:
            if AlumnoCurso.objects.filter(
                alumno_id=retrieved_alumno.pk,
                anio_lectivo_id=anio_corriente.pk,
            ):
                data = {
                    "detail": "No se puede eliminar un alumno que esté cursando actualmente"
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST,)

        retrieved_alumno.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_alumnos",
        operation_description="""
        Crear varios Alumnos al mismo tiempo.
        Se debe mandar una lista de objetos, por más que se esté creando sólo un alumno.
        Los alumnos creados no deben tener DNIs iguales entre ellos ni iguales con alumnos ya existentes.
        Se pueden modificar los siguientes campos:
        -  dni (debe estar disponible y es obligatorio)
        -  nombre (obligatorio)
        -  apellido (obligatorio)
        -  email
        -  legajo
        -  fecha_nacimiento
        -  direccion
        -  localidad
        -  provincia
        -  fecha_inscripcion
        """,
        request_body=serializers.CreateAlumnoSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        if type(request.data) is not list:
            return Response(
                data={"detail": "Debe mandarse una lista de alumnos"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        institucion = request.user.institucion
        data = request.data
        for alumno in data:
            alumno["institucion"] = institucion.id
        serializer = serializers.CreateAlumnoSerializer(
            data=request.data, many=True
        )
        if serializer.is_valid():
            for alumno in serializer.validated_data:
                try:
                    # TODO optimize with a single query
                    Alumno.objects.get(dni=alumno.get("dni"))
                except Alumno.DoesNotExist:
                    continue
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(
                    data={"detail": "Alumno con el mismo dni existente"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(
                set([alumno["dni"] for alumno in serializer.validated_data])
            ) != len(serializer.validated_data):
                return Response(
                    data={"detail": "Alumnos con el mismo dni en conflicto"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                serializer.save()
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ids = {
                b.dni: b.id
                for b in Alumno.objects.filter(
                    dni__in=[a.get("dni") for a in serializer.validated_data]
                )
            }
            return Response(data=ids, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


create_alumno = AlumnoViewSet.as_view({"post": "create"})
list_alumno = AlumnoViewSet.as_view({"get": "list"})
mix_alumno = AlumnoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)


class AlumnoCursoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumnocurso")]
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

    alumno_parameter = openapi.Parameter(
        "alumno",
        openapi.IN_QUERY,
        description="Alumno por el que queremos filtrar la búsqueda",
        type=openapi.TYPE_INTEGER,
    )

    @swagger_auto_schema(
        operation_id="get_alumno_curso",
        operation_description="""
        Obtener un AlumnoCurso utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        alumno_curso = get_object_or_404(AlumnoCurso, pk=pk)
        if alumno_curso.alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAlumnoCursoSerializer(
            alumno_curso, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_alumo_curso",
        operation_description="""
        Listar los AlumnoCurso de la institución.
        Se pueden pasar por query params curso (id del curso), el anio_lectivo (id del anio_lectivo) y el alumno (id del alumno).
        Ninguno de los parámetros es obligatorio y se pueden usar todos al mismo tiempo para restringir más el listado.
        """,
        manual_parameters=[
            anio_lectivo_parameter,
            curso_parameter,
            alumno_parameter,
        ],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        queryset = AlumnoCurso.objects.filter(
            alumno__institucion__exact=request.user.institucion
        )
        curso = request.query_params.get("curso", None)
        anio_lectivo = request.query_params.get("anio_lectivo", None)
        alumno = request.query_params.get("alumno", None)

        if curso:
            if curso.isnumeric():
                curso = int(curso)
            else:
                return Response(
                    data={"curso": "El valor no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            curso_retrieved = get_object_or_404(Curso, pk=curso)

            if (
                curso_retrieved.anio.carrera.institucion
                != request.user.institucion
            ):
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(curso__pk__exact=curso)

        if alumno:
            if alumno.isnumeric():
                alumno = int(alumno)
            else:
                return Response(
                    data={"alumno": "El valor no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumno_retrieved = get_object_or_404(Alumno, pk=alumno)

            if alumno_retrieved.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(alumno__pk__exact=alumno)

        if anio_lectivo:
            if anio_lectivo.isnumeric():
                anio_lectivo = int(anio_lectivo)
            else:
                return Response(
                    data={"anio_lectivo": "El valor no es numérico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            anio_lectivo_retrieved = get_object_or_404(
                AnioLectivo, pk=anio_lectivo
            )

            if anio_lectivo_retrieved.institucion != request.user.institucion:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            queryset = queryset.filter(anio_lectivo__pk__exact=anio_lectivo)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewAlumnoCursoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewAlumnoCursoSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="delete_alumno_curso",
        operation_description="Borrar un AlumnoCurso utilizando su id.",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        retrieved_alumno_curso = get_object_or_404(AlumnoCurso, pk=pk)
        if (
            retrieved_alumno_curso.alumno.institucion
            != request.user.institucion
        ):
            return Response(status=status.HTTP_404_NOT_FOUND)
        retrieved_alumno_curso.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_alumno_curso",
        operation_description="""
        Crear un AlumnoCurso (Asignar un Alumno a un Curso específico para un Año Lectivo).
        No se puede asignar un alumno a dos cursos distintos en un Año Lectivo.
        Todos los campos son obligatorios y son:
        -  alumno (id del alumno)
        -  curso (id del curso)
        -  anio_lectivo (id del anio_lectivo)
        """,
        request_body=serializers.CreateAlumnoCursoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.CreateAlumnoCursoSerializer(
            data=request.data, many=False
        )
        if serializer.is_valid():
            alumno = get_object_or_404(
                Alumno, pk=serializer.validated_data["alumno"].pk
            )
            curso = get_object_or_404(
                Curso, pk=serializer.validated_data["curso"].pk
            )
            anio_lectivo = get_object_or_404(
                AnioLectivo, pk=serializer.validated_data["anio_lectivo"].pk
            )
            if (
                len(
                    set(
                        [
                            request.user.institucion,
                            alumno.institucion,
                            anio_lectivo.institucion,
                            curso.anio.carrera.institucion,
                        ]
                    )
                )
                != 1
            ):
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if (
                len(
                    AlumnoCurso.objects.filter(
                        alumno__exact=alumno, anio_lectivo__exact=anio_lectivo
                    )
                )
                != 0
            ):
                return Response(
                    data={
                        "detail": "No se puede asignar un alumno a dos cursos distintos en un Año Lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            for item in serializer.errors.values():
                if item[0].code == "does_not_exist":
                    return Response(
                        data={"detail": "No encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="create_multile_alumno_curso",
        operation_description="""
        Crear multiples AlumnoCurso (Asignar un Alumno a un Curso específico para un Año Lectivo).
        No se puede asignar un alumno a dos cursos distintos en un Año Lectivo.
        Todos los campos son obligatorios y son:
        -  alumno (id del alumno)
        -  curso (id del curso)
        -  anio_lectivo (id del anio_lectivo)
        """,
        request_body=serializers.CreateAlumnoCursoSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["POST"], name="create_multiple")
    def create_multiple(self, request):
        serializer = serializers.CreateAlumnoCursoSerializer(
            data=request.data, many=True
        )
        if serializer.is_valid():
            if len(serializer.validated_data) == 0:
                return Response(
                    data={"detail": "No se recibió ninguna información"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cursos = list(
                set([a.get("curso") for a in serializer.validated_data])
            )
            if len(cursos) != 1:
                return Response(
                    data={
                        "detail": "No se puede asignar a distintos cursos en una misma llamada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            anios_lectivos = list(
                set([a.get("anio_lectivo") for a in serializer.validated_data])
            )
            if len(anios_lectivos) != 1:
                return Response(
                    data={
                        "detail": "No se puede asignar a distintos Años Lectivos en una misma llamada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumnos = [a.get("alumno") for a in serializer.validated_data]
            if len(set(a.id for a in alumnos)) != len(alumnos):
                return Response(
                    data={
                        "detail": "No se puede asignar más de una vez a un Alumno en una misma llamada"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            institucion_alumnos = list(set(a.institucion for a in alumnos))
            if len(institucion_alumnos) != 1:
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if (
                len(
                    set(
                        [
                            request.user.institucion,
                            institucion_alumnos[0],
                            anios_lectivos[0].institucion,
                            cursos[0].anio.carrera.institucion,
                        ]
                    )
                )
                != 1
            ):
                return Response(
                    data={"detail": "No encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            for alumno in alumnos:
                if (
                    len(
                        AlumnoCurso.objects.filter(
                            alumno__exact=alumno,
                            anio_lectivo__exact=anios_lectivos[0],
                        )
                    )
                    != 0
                ):
                    return Response(
                        data={
                            "detail": "No se puede asignar un alumno a dos cursos distintos en un Año Lectivo"
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
        operation_id="delete_multiple_alumno_curso",
        operation_description="Borrar multiples AlumnoCurso",
        request_body=serializers.CreateAlumnoCursoSerializer(many=True),
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["DELETE"], name="delete_multiple")
    def delete_multiple(self, request):
        serializer = serializers.CreateAlumnoCursoSerializer(
            many=True, data=request.data
        )
        if serializer.is_valid():
            for alumno_curso in serializer.validated_data:
                alumno_c = AlumnoCurso.objects.filter(
                    alumno__exact=alumno_curso.get("alumno"),
                    curso__exact=alumno_curso.get("curso"),
                    anio_lectivo__exact=alumno_curso.get("anio_lectivo"),
                    alumno__institucion__exact=request.user.institucion,
                )
                if len(alumno_c) >= 1:
                    alumno_c[0].delete()

            return Response(status=status.HTTP_200_OK)

        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_alumno_curso = AlumnoCursoViewSet.as_view({"post": "create"})
multiple_alumno_curso = AlumnoCursoViewSet.as_view(
    {"post": "create_multiple", "delete": "delete_multiple"}
)
list_alumno_curso = AlumnoCursoViewSet.as_view({"get": "list"})
mix_alumno_curso = AlumnoCursoViewSet.as_view(
    {"get": "get", "delete": "destroy"}
)
