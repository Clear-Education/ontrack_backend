from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import anio as serializers_anio
from curricula.api.serializers import carrera as serializers_carrera
from curricula.models import Anio, Curso, Carrera
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


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
            instance = serializer.create()
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
            serializer.update(anio, serializer.validated_data)
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
        queryset = Anio.objects.all()
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
            serializer.update(curso, serializer.validated_data)
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
        curso = get_object_or_404(self.get_queryset(), pk=pk)
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
