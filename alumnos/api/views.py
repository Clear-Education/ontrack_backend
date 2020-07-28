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


class AlumnoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumno")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAlumnoSerializer()}
    OK_LIST = {200: serializers.ViewAlumnoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        alumno = get_object_or_404(Alumno, pk=pk)
        if alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAlumnoSerializer(alumno, many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        queryset = Alumno.objects.filter(
            institucion__exact=request.user.institucion
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewAlumnoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewAlumnoSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.UpdateAlumnoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
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
            serializer.update(retrieved_alumno)
            return Response(status=status.HTTP_200_OK,)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        if retrieved_alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND,)
        retrieved_alumno.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
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

            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS})
    def get(self, request, pk=None):
        alumno_curso = get_object_or_404(AlumnoCurso, pk=pk)
        if alumno_curso.alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAlumnoCursoSerializer(
            alumno_curso, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[anio_lectivo_parameter, curso_parameter],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        queryset = AlumnoCurso.objects.filter(
            alumno__institucion__exact=request.user.institucion
        )
        curso = request.query_params.get("curso", None)
        anio_lectivo = request.query_params.get("anio_lectivo", None)
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

        if curso and anio_lectivo:
            queryset = queryset.filter(
                anio_lectivo__pk__exact=anio_lectivo, curso__pk__exact=curso
            )
        elif anio_lectivo and not curso:
            queryset = queryset.filter(anio_lectivo__pk__exact=anio_lectivo)
        elif curso and not anio_lectivo:
            queryset = queryset.filter(curso__pk__exact=curso)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewAlumnoCursoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewAlumnoCursoSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS})
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
                        alumno=alumno, anio_lectivo=anio_lectivo
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


create_alumno_curso = AlumnoCursoViewSet.as_view({"post": "create"})
list_alumno_curso = AlumnoCursoViewSet.as_view({"get": "list"})
mix_alumno_curso = AlumnoCursoViewSet.as_view(
    {"get": "get", "delete": "destroy"}
)
