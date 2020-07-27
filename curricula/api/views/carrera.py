from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import carrera as serializers
from curricula.models import Carrera
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


class CarreraViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("carrera")]
    queryset = Carrera.objects.all()
    OK_CREATED = {201: responses.CreatedSerializer}
    OK_EMPTY = {200: ""}
    OK_LIST = {200: serializers.ViewCarreraSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewCarreraSerializer()}

    @swagger_auto_schema(
        request_body=serializers.CreateCarreraSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
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
            institucion = serializer.create(institucion)
            data = {"id": institucion.id}
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.EditCarreraSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar Carrera
        """
        carrera = get_object_or_404(
            self.get_queryset(),
            pk=pk,
            institucion_id=request.user.institucion.id,
        )
        serializer = serializers.EditCarreraSerializer(
            data=request.data, partial=True
        )
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
        carrera = get_object_or_404(
            queryset, pk=pk, institucion_id=request.user.institucion.id
        )
        carrera.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Carreras
        """
        queryset = Carrera.objects.filter(
            institucion_id=request.user.institucion.id
        )
        serializer = serializers.ViewCarreraSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver una institucion
        """
        queryset = Carrera.objects.all()
        carrera = get_object_or_404(
            queryset, pk=pk, institucion_id=request.user.institucion.id
        )
        serializer = serializers.ViewCarreraSerializer(carrera)
        return Response(serializer.data)


create_carrera = CarreraViewSet.as_view({"post": "create"})
list_carrera = CarreraViewSet.as_view({"get": "list"})
view_edit_carrera = CarreraViewSet.as_view(
    {"get": "get", "delete": "destroy", "patch": "update"}
)
