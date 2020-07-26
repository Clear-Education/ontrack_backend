from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import materia as serializers
from curricula.models import Materia, Anio
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from drf_yasg import openapi


class MateriaViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated, permission_required("materia")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewMateriaSerializer()}
    OK_LIST = {200: serializers.ViewMateriaSerializer(many=True)}
    OK_CREATED = {201: responses.CreatedSerializer}
    anio_param = openapi.Parameter(
        "anio",
        openapi.IN_QUERY,
        description="Anio para el que queremos listar sus Materias",
        type=openapi.TYPE_INTEGER,
    )

    def get_queryset(self, institucion):
        """
        Restringir la busqueda de Materias por un año
        """
        queryset = Materia.objects.filter(
            anio__carrera__institucion=institucion
        )
        anio = self.request.query_params.get("anio", None)
        if anio is not None:
            queryset = queryset.filter(anio=anio,)
        return queryset

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver una materia
        """
        materia = get_object_or_404(Materia, pk=pk)
        if materia.anio.carrera.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewMateriaSerializer(materia)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[anio_param],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, anio_id=None):
        """
        Listar las materias de un anio
        """
        get_object_or_404(
            Anio.objects.filter(
                carrera__institucion_id=request.user.institucion.id
            ),
            pk=anio_id,
        )
        materia_list = Materia.objects.filter(
            anio_id=anio_id,
            anio__carrera__institucion_id=request.user.institucion.id,
        )
        serializer = serializers.ViewMateriaSerializer(materia_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.CreateMateriaSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear una materia
        """
        serializer = serializers.CreateMateriaSerializer(request.data)
        data = {}

        if serializer.is_valid():
            materia = serializer.create()
            data = {"id": materia.id}
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.EditMateriaSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Actualizar los datos de una materia
        """
        materia = get_object_or_404(self.get_queryset(), pk=pk,)
        serializer = serializers.EditMateriaSerializer(
            data=request.data, partial=True
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            materia = serializer.update(materia, serializer.validated_data)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Eliminar una Materia
        """
        materia = get_object_or_404(Materia, pk=pk)
        if materia.anio.carrera.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        materia.delete()
        return Response(status=status.HTTP_200_OK)


view_edit_materia = MateriaViewSet.as_view(
    {"get": "get", "delete": "destroy", "patch": "update"}
)
list_materia = MateriaViewSet.as_view({"get": "list"})
create_materia = MateriaViewSet.as_view({"post": "create"})
