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
from alumnos.models import Alumno, AlumnoCurso


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
                try:
                    Alumno.objects.get(
                        dni=serializer.validated_data.get("dni")
                    )
                    return Response(
                        data={"detail": "Alumno con el mismo dni existente"},
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
        request_body=serializers.CreateAlumnoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
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

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS})
    def get(self, request, pk=None):
        alumno_curso = get_object_or_404(AlumnoCurso, pk=pk)
        if alumno_curso.alumno.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAlumnoCursoSerializer(
            alumno_curso, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS})
    def list(self, request):
        queryset = AlumnoCursoViewSet.objects.filter(
            alumno__institucion__exact=request.user.institucion
        )
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
                Alumno, pk=serializer.validated_data["alumno"]
            )
            curso = get_object_or_404(
                Curso, pk=serializer.validated_data["curso"]
            )
            anio_lectivo = get_object_or_404(
                AnioLectivo, pk=serializer.validated_data["anio_lectivo"]
            )
            if (
                len(
                    set(
                        request.user.institucion,
                        alumno.institucion,
                        anio_lectivo.institucion,
                        curso.anio.carrera.institucion,
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
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_alumno_curso = AlumnoCursoViewSet.as_view({"post": "create"})
list_alumno_curso = AlumnoCursoViewSet.as_view({"get": "list"})
mix_alumno_curso = AlumnoCursoViewSet.as_view(
    {"get": "get", "delete": "destroy"}
)
