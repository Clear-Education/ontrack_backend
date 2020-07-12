from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from instituciones.api import serializers
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


CREATED_REPONSE = {201: ""}

OK_RESPONSE = {200: serializers.InstitucionSerializer}

OK_LIST = {200: serializers.InstitucionSerializer(many=True)}

OK_EMPTY = {200: ""}


class InstitucionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("institucion")]
    pagination_class = LimitOffsetPagination
    queryset = Institucion.objects.all()
    serializer_class = serializers.InstitucionSerializer

    @swagger_auto_schema(
        request_body=serializers.CreateInstitucionSerializer,
        responses={**CREATED_REPONSE, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear nueva Institucion
        """
        serializer = serializers.CreateInstitucionSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.CreateInstitucionSerializer,
        responses={**OK_RESPONSE, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar Institucion
        """
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        serializer = serializers.CreateInstitucionSerializer(
            institucion, data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid():
            serializer.update(institucion, serializer.validated_data)
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Elimina una institucion
        """
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        institucion.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.InstitucionStatusSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    @action(detail=False, methods=["PATCH"], name="status")
    def status(self, request, pk=None):
        """
        Cambiar el estado de una institucion
        """
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        serializer = serializers.InstitucionStatusSerializer(
            instance=institucion, data=request.data
        )
        if serializer.is_valid():
            serializer.update(institucion, serializer.validated_data)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Instituciones
        """
        queryset = Institucion.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, pk=None):
        """
        Ver una institucion
        """
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        serializer = serializers.InstitucionSerializer(institucion)
        return Response(serializer.data)


create_institucion = InstitucionViewSet.as_view({"post": "create"})
update_institucion = InstitucionViewSet.as_view(
    {"patch": "update", "delete": "destroy", "get": "get"}
)
status_institucion = InstitucionViewSet.as_view({"patch": "status"})
list_institucion = InstitucionViewSet.as_view({"get": "list"})
