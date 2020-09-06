from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import anio as serializers_anio
from curricula.api.serializers import carrera as serializers_carrera
from curricula.models import Anio, Curso, Carrera, Materia
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from django.core.exceptions import ValidationError


class AnioViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("anio")]
    queryset = Anio.objects.all()
    OK_CREATED = {201: responses.CreatedSerializer}
    OK_EMPTY = {200: ""}
    OK_LIST = {200: serializers_anio.AnioSerializer(many=True)}
    OK_VIEW = {200: serializers_anio.AnioSerializer()}

    @swagger_auto_schema(
        request_body=serializers_anio.CreateAnioSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un anio con sus cursos (opcional)
        """
        serializer = serializers_anio.CreateAnioSerializer(data=request.data)
        data = {}

        if serializer.is_valid(raise_exception=True):
            try:
                instance = serializer.create()
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {"id": instance.id}
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers_carrera.EditCarreraSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar un anio, sin afectar sus cursos (se editan aparte)
        """
        anio = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers_anio.EditAnioSerializer(
            data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.update(anio, serializer.validated_data)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response_serializer = serializers_anio.AnioSerializer(anio)
            data = response_serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Elimina un Anio
        """
        queryset = Anio.objects.all()
        anio = get_object_or_404(queryset, pk=pk)
        if Curso.objects.filter(anio=anio).count() != 0:
            data = {
                "detail": "No se puede eliminar un año que ya contenga cursos!"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if Materia.objects.filter(anio=anio).count() != 0:
            data = {
                "detail": "No se puede eliminar un año que ya contenga materias!"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        anio.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request, carrera_id=None):
        """
        Listar Anios
        """
        get_object_or_404(
            Carrera.objects.filter(institucion_id=request.user.institucion.id),
            pk=carrera_id,
        )
        queryset = Anio.objects.filter(
            carrera_id=carrera_id,
            carrera__institucion_id=request.user.institucion.id,
        )
        serializer = serializers_anio.AnioSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver un anio
        """
        queryset = Anio.objects.filter(
            carrera__institucion_id=request.user.institucion.id
        )
        anio = get_object_or_404(queryset, pk=pk)
        serializer = serializers_anio.AnioSerializer(anio)
        return Response(serializer.data)


create_anio = AnioViewSet.as_view({"post": "create"})
view_edit_anio = AnioViewSet.as_view(
    {"get": "get", "delete": "destroy", "patch": "update"}
)
list_anio = AnioViewSet.as_view({"get": "list"})


class CursoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("curso")]
    queryset = Curso.objects.all()
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers_anio.CursoSerializer()}
    OK_LIST = {200: serializers_anio.CursoSerializer(many=True)}
    OK_CREATED = {201: serializers_anio.CursoSerializer()}

    @swagger_auto_schema(
        request_body=serializers_anio.CreateSingleCursoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un curso
        """

        serializer = serializers_anio.CreateSingleCursoSerializer(
            data=request.data
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            get_object_or_404(
                Anio.objects.filter(
                    carrera__institucion_id=request.user.institucion.id
                ),
                pk=serializer.validated_data["anio"].pk,
            )
            try:
                instance = serializer.create()
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        s = serializers_anio.CursoSerializer(instance=instance)
        return Response(data=s.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Elimina un Curso
        """
        curso = get_object_or_404(self.get_queryset(), pk=pk)
        curso.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers_anio.EditCursoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Edita un curso
        """
        curso = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers_anio.EditCursoSerializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.update(curso, serializer.validated_data)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response_serializer = serializers_anio.CursoSerializer(curso)
            data = response_serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver un curso
        """
        queryset = Curso.objects.filter(
            anio__carrera__institucion_id=request.user.institucion.id
        )
        curso = get_object_or_404(queryset, pk=pk)
        serializer = serializers_anio.CursoSerializer(curso)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request, anio_id=None):
        """
        Listar Cursos de un Anio
        """
        get_object_or_404(
            Anio.objects.filter(
                carrera__institucion_id=request.user.institucion.id
            ),
            pk=anio_id,
        )
        queryset = Curso.objects.filter(
            anio_id=anio_id,
            anio__carrera__institucion_id=request.user.institucion.id,
        )
        serializer = serializers_anio.CursoSerializer(queryset, many=True)
        return Response(serializer.data)


view_edit_curso = CursoViewSet.as_view(
    {"get": "get", "delete": "destroy", "patch": "update"}
)
list_curso = CursoViewSet.as_view({"get": "list"})
create_curso = CursoViewSet.as_view({"post": "create"})
