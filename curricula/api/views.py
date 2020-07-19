from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from curricula.api import serializers
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


class CarreraViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("carrera")]
    queryset = Carrera.objects.all()
    OK_CREATED = {201: ""}
    OK_EMPTY = {200: ""}
    OK_LIST = {200: serializers.ViewCarreraSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewCarreraSerializer()}

    @swagger_auto_schema(
        request_body=serializers.CreateCarreraSerializer, responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear una Carrera
        """
        serializer = serializers.CreateCarreraSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            id_institucion = request.user.institucion.id
            institucion = Institucion.objects.get(pk=id_institucion)
            serializer.create(institucion)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.EditCarreraSerializer, responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar Carrera
        """
        carrera = get_object_or_404(self.get_queryset(), pk=pk, institucion_id=request.user.institucion.id,)
        serializer = serializers.EditCarreraSerializer(data=request.data, partial=True)
        data = {}
        if serializer.is_valid(raise_exception=True):
            carrera = serializer.update(carrera, serializer.validated_data)
            response_serializer = serializers.ViewCarreraSerializer(carrera)
            data = response_serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Elimina una carrera
        """
        queryset = Carrera.objects.all()
        carrera = get_object_or_404(queryset, pk=pk, institucion_id=request.user.institucion.id)
        carrera.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Carreras
        """
        queryset = Carrera.objects.filter(institucion_id=request.user.institucion.id)
        serializer = serializers.ViewCarreraSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver una institucion
        """
        queryset = Carrera.objects.all()
        carrera = get_object_or_404(queryset, pk=pk, institucion_id=request.user.institucion.id)
        serializer = serializers.ViewCarreraSerializer(carrera)
        return Response(serializer.data)


# Vistas CARRERA

create_carrera = CarreraViewSet.as_view({"post": "create"})
list_carrera = CarreraViewSet.as_view({"get": "list"})
view_edit_carrera = CarreraViewSet.as_view({"get": "get", "delete": "destroy", "patch": "update"})


class AnioViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("anio")]
    queryset = Anio.objects.all()
    OK_CREATED = {201: ""}
    OK_EMPTY = {200: ""}
    OK_LIST = {200: serializers.AnioSerializer(many=True)}
    OK_VIEW = {200: serializers.AnioSerializer()}

    @swagger_auto_schema(
        request_body=serializers.CreateAnioSerializer, responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un anio con sus cursos (opcional)
        """
        serializer = serializers.CreateAnioSerializer(data=request.data)
        data = {}

        if serializer.is_valid(raise_exception=True):
            serializer.create()
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.EditCarreraSerializer, responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar un anio, sin afectar sus cursos (se editan aparte)
        """
        anio = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.EditAnioSerializer(data=request.data, partial=True)
        data = {}
        if serializer.is_valid(raise_exception=True):
            serializer.update(anio, serializer.validated_data)
            response_serializer = serializers.AnioSerializer(anio)
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
        queryset = Anio.objects.filter(carrera_id=carrera_id, carrera__institucion_id=request.user.institucion.id,)
        serializer = serializers.AnioSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver un anio
        """
        queryset = Anio.objects.all()
        anio = get_object_or_404(queryset, pk=pk)
        serializer = serializers.AnioSerializer(anio)
        return Response(serializer.data)


create_anio = AnioViewSet.as_view({"post": "create"})
view_edit_anio = AnioViewSet.as_view({"get": "get", "delete": "destroy", "patch": "update"})
list_anio = AnioViewSet.as_view({"get": "list"})


class CursoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("curso")]
    queryset = Curso.objects.all()
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.CursoSerializer()}

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Elimina un Curso
        """
        curso = get_object_or_404(self.get_queryset(), pk=pk)
        curso.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.EditCursoSerializer, responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Edita un curso
        """
        curso = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.EditCursoSerializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            serializer.update(curso, serializer.validated_data)
            response_serializer = serializers.CursoSerializer(curso)
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
        serializer = serializers.CursoSerializer(curso)
        return Response(serializer.data)


view_edit_curso = CursoViewSet.as_view({"get": "get", "delete": "destroy", "patch": "update"})


class AnioLectivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("aniolectivo")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAnioLectivoSerializer()}
    OK_LIST = {200: serializers.ViewAnioLectivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAnioLectivoSerializer(anio_lectivo)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        anio_lectivo_list = AnioLectivo.objects.filter(institucion__exact=request.user.institucion)
        serializer = serializers.ViewAnioLectivoSerializer(anio_lectivo_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.EditAnioLectivoSerializer, responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.EditAnioLectivoSerializer(data=request.data)
        serializer.get_existing_anio_lectivo(anio_lectivo)
        if serializer.is_valid():
            updated_anio_lectivo = {
                "nombre": serializer.validated_data.get("nombre", anio_lectivo.nombre),
                "fecha_desde": serializer.validated_data.get("fecha_desde", anio_lectivo.fecha_desde),
                "fecha_hasta": serializer.validated_data.get("fecha_hasta", anio_lectivo.fecha_hasta),
            }
            for institucion_retrieved in AnioLectivo.objects.filter(
                institucion__exact=request.user.institucion
            ).exclude(id__exact=anio_lectivo.id):
                if (
                    (
                        institucion_retrieved.fecha_desde <= updated_anio_lectivo["fecha_desde"]
                        and institucion_retrieved.fecha_hasta >= updated_anio_lectivo["fecha_desde"]
                    )
                    or (
                        institucion_retrieved.fecha_desde <= updated_anio_lectivo["fecha_hasta"]
                        and institucion_retrieved.fecha_hasta >= updated_anio_lectivo["fecha_hasta"]
                    )
                    or (
                        updated_anio_lectivo["fecha_desde"] <= institucion_retrieved.fecha_desde
                        and updated_anio_lectivo["fecha_hasta"] >= institucion_retrieved.fecha_hasta
                    )
                ):
                    return Response(
                        data={
                            "detail": "Las fechas entran en conflicto con el Año Lectivo de nombre "
                            + institucion_retrieved.nombre
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            serializer.update(anio_lectivo)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        anio_lectivo.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.AnioLectivoSerializer, responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.AnioLectivoSerializer(data=request.data)
        if serializer.is_valid():
            for institucion_retrieved in AnioLectivo.objects.filter(institucion__exact=request.user.institucion):
                if (
                    (
                        institucion_retrieved.fecha_desde <= serializer.validated_data["fecha_desde"]
                        and institucion_retrieved.fecha_hasta >= serializer.validated_data["fecha_desde"]
                    )
                    or (
                        institucion_retrieved.fecha_desde <= serializer.validated_data["fecha_hasta"]
                        and institucion_retrieved.fecha_hasta >= serializer.validated_data["fecha_hasta"]
                    )
                    or (
                        serializer.validated_data["fecha_desde"] <= institucion_retrieved.fecha_desde
                        and serializer.validated_data["fecha_hasta"] >= institucion_retrieved.fecha_hasta
                    )
                ):
                    return Response(
                        data={
                            "detail": "Las fechas entran en conflicto con el Año Lectivo de nombre "
                            + institucion_retrieved.nombre
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            serializer.create(request.user.institucion)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


create_anio_lectivo = AnioLectivoViewSet.as_view({"post": "create"})
list_anio_lectivo = AnioLectivoViewSet.as_view({"get": "list"})
update_anio_lectivo = AnioLectivoViewSet.as_view({"get": "get", "patch": "update", "delete": "destroy"})


class AlumnoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("alumno")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAnioLectivoSerializer()}
    OK_LIST = {200: serializers.ViewAnioLectivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        pass

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        pass

    @swagger_auto_schema(
        request_body=serializers.EditAnioLectivoSerializer, responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        pass

    @swagger_auto_schema(
        request_body=serializers.AnioLectivoSerializer, responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass


create_alumno = AnioLectivoViewSet.as_view({"post": "create"})
list_alumno = AnioLectivoViewSet.as_view({"get": "list"})
mix_alumno = AnioLectivoViewSet.as_view({"get": "get", "patch": "update", "delete": "destroy"})
