from rest_framework.viewsets import ModelViewSet, ViewSet
from seguimientos.api import serializers
from seguimientos.models import Seguimiento, IntegranteSeguimiento
from seguimientos.models import RolSeguimiento
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from rest_framework.pagination import LimitOffsetPagination


class SeguimientoViewSet(ViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("seguimiento"),
    ]

    OK_LIST = {200: serializers.ListSeguimientoSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewSeguimientoSerializer}
    OK_CREATED = {201: serializers.ViewSeguimientoSerializer}
    OK_EMPTY = {200: ""}

    @swagger_auto_schema(
        request_body=serializers.CreateSeguimientoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un Seguimiento
        """
        serializer = serializers.CreateSeguimientoSerializer(
            data=request.data, context={"request": request}
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            s = serializer.create(serializer.validated_data)
            s = Seguimiento.objects.get(pk=s.pk)
            view_serializer = serializers.ViewSeguimientoSerializer(instance=s)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data=view_serializer.data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        request_body=serializers.EditSeguimientoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar un seguimiento

        Editable:
            - nombre
            - descripcion
            - fecha_cierre
            - integrantes
            - estado
        """
        pass

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Eliminar un Seguimiento
        """
        pass

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Seguimientos (Paginado!)
        Campos que se muestran:
            - nombre
            - descripcion
            - estado
            - fecha_inicio
            - fecha_cierre
        """
        pass

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver un seguimiento (ignorar parámetros de paginado)
        Campos que se muestran:
            - nombre
            - descripcion
            - estado
            - fecha_inicio
            - fecha_cierre
            - alumnos
            - integrantes
            - materias
            - institucion
            - anio_lectivo
            - en_progreso
        """
        pass


class RolSeguimientoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("rolseguimiento"),
    ]
    queryset = RolSeguimiento.objects.all()
    serializer_class = serializers.CreateSeguimientoSerializer
    pagination_class = LimitOffsetPagination
    CREATED_RESPONSE = {201: serializers.CreateRolSerializer}
    OK_LIST = {200: serializers.ViewRolSerializer(many=True)}
    OK_EMPTY = {200: ""}

    @swagger_auto_schema(
        request_body=serializers.CreateRolSerializer,
        responses={**CREATED_RESPONSE, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un Rol de Seguimiento
        """
        serializer = serializers.CreateRolSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.CreateRolSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar un Rol de Seguimiento
        """
        queryset = RolSeguimiento.objects.all()
        rol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.CreateRolSerializer(
            rol, data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid():
            serializer.update(rol, serializer.validated_data)
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Eliminar un Rol de Seguimiento
        """
        queryset = RolSeguimiento.objects.all()
        rol = get_object_or_404(queryset, pk=pk)
        rol.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Roles de Seguimiento

        """
        queryset = RolSeguimiento.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, pk=None):
        """
        Ver un Rol de Seguimiento
        """
        queryset = RolSeguimiento.objects.all()
        rol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.ViewRolSerializer(rol)
        return Response(serializer.data)


list_seguimiento = SeguimientoViewSet.as_view({"get": "list"})
view_edit_seguimiento = SeguimientoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
create_seguimiento = SeguimientoViewSet.as_view({"post": "create"})


list_rol = RolSeguimientoViewSet.as_view({"get": "list"})
view_edit_rol = RolSeguimientoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
create_rol = RolSeguimientoViewSet.as_view({"post": "create"})
