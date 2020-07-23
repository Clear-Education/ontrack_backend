from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import materia as serializers
from curricula.models import Materia
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


class MateriaViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated, permission_required("materia")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewMateriaSerializer()}
    OK_LIST = {200: serializers.ViewMateriaSerializer(many=True)}
    OK_CREATED = {201: responses.CreatedSerializer}

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

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar las materias de la institucion del usuario logeado
        """
        materia_list = Materia.objects.filter(
            anio__carrera__institucion=request.user.institucion
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


view_edit_materia = MateriaViewSet.as_view({"get": "get", "delete": "destroy"})
list_materia = MateriaViewSet.as_view({"get": "list"})
create_materia = MateriaViewSet.as_view({"post": "create"})
