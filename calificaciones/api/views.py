from rest_framework.viewsets import ModelViewSet
from calificaciones.api import serializers
from curricula.models import Carrera
from calificaciones.models import Calificacion
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


class CalificacionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("calificacion")]
    queryset = Calificacion.objects.all()
    OK_CREATED = {201: responses.CreatedSerializer}
    OK_CREATED_MULTIPLE = {201: ""}

    OK_EMPTY = {200: ""}
    # OK_LIST = {200: serializers.ViewCarreraSerializer(many=True)}
    # OK_VIEW = {200: serializers.ViewCarreraSerializer()}

    @swagger_auto_schema(
        request_body=serializers.CreateCalificacionSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crea una sola calificacion
        """
        serializer = serializers.CreateCalificacionSerializer(
            data=request.data
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            institucion_alumno = serializer.validated_data[
                "alumno"
            ].institucion_id
            if institucion_alumno != request.user.institucion_id:
                return Response(status=status.HTTP_404_NOT_FOUND)
            calificacion = serializer.create()
            data = {"id": calificacion.pk}
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.CreateCalificacionListSerializer,
        responses={**OK_CREATED_MULTIPLE, **responses.STANDARD_ERRORS},
    )
    def create_multiple(self, request):
        """
        Crea una multiples calificaciones
        """
        serializer = serializers.CreateCalificacionListSerializer(
            data=request.data, context={"request": request}
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


create_calificaciones = CalificacionViewSet.as_view({"post": "create"})
create_calificaciones_multiple = CalificacionViewSet.as_view(
    {"post": "create_multiple"}
)

