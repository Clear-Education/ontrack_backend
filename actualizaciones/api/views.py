from rest_framework.viewsets import ModelViewSet
from actualizaciones.api import serializers
from seguimientos.models import Seguimiento, IntegranteSeguimiento
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
import os
from django.db import transaction

# from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses
from actualizaciones.models import Actualizacion, ActualizacionAdjunto
from datetime import datetime, timedelta

# from curricula.models import Carrera, Anio, Curso, AnioLectivo
# from instituciones.models import Institucion
# from users.models import User
# from alumnos.models import Alumno, AlumnoCurso
# from django.core.validators import validate_integer
# from itertools import chain
# from django.core.exceptions import ValidationError
# import datetime
# from rest_framework.decorators import action


class ActualizacionViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("actualizacion"),
    ]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.GetActualizacionSerializer()}
    OK_LIST = {200: serializers.GetActualizacionSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="get_actualizacion",
        operation_description="""
        Obtener un Actualizacion utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, actualizacion_pk=None):
        actualizacion = get_object_or_404(Actualizacion, pk=actualizacion_pk)
        if actualizacion.seguimiento.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        integrante = IntegranteSeguimiento.objects.filter(
            seguimiento__exact=actualizacion.seguimiento,
            usuario__exact=request.user,
            fecha_hasta__isnull=True,
        )

        if not len(integrante):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = serializers.GetActualizacionSerializer(
            actualizacion, many=False
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_actualizacion",
        operation_description="""
        Listar las actualizaciones de un seguimiento utilizando el id de seguimiento.
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, seguimiento_pk=None):
        try:
            seguimiento = Seguimiento.objects.get(id__exact=seguimiento_pk)
        except Seguimiento.DoesNotExist:
            return Response(
                data={"detail": "El seguimiento indicado no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        integrante = IntegranteSeguimiento.objects.filter(
            seguimiento__exact=seguimiento,
            usuario__exact=request.user,
            fecha_hasta__isnull=True,
        )

        if not len(integrante):
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = Actualizacion.objects.filter(
            seguimiento__id__exact=seguimiento_pk,
        ).order_by("-fecha_creacion")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.GetActualizacionSerializer(
                page, many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = serializers.GetActualizacionSerializer(
            queryset, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_actualizacion",
        operation_description="""
        Modificar una Actualización utilizando su id.

        Solo se puede modificar el cuerpo de la misma.
        Sólo se puede modificar si es el creado, el seguimiento está en progreso y no han
        pasado más de 30 minutos desde su creación.
        """,
        request_body=serializers.UpdateActualizacionSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, actualizacion_pk=None):
        try:
            actualizacion = Actualizacion.objects.get(id=actualizacion_pk)
        except Actualizacion.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            integrante = IntegranteSeguimiento.objects.get(
                seguimiento__exact=actualizacion.seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )
        except IntegranteSeguimiento.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not actualizacion.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se puede modificar una actualización para un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actualizacion.usuario != request.user:
            return Response(
                data={
                    "detail": "No puede modificar una actualización que usted no creó"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actualizacion.fecha_modificacion < datetime.now() - timedelta(
            minutes=30
        ):
            return Response(
                data={
                    "detail": "No se puede modificar una actualización luego de que pasaron 30 minutos desde su última modificación"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializers.CreateActualizacionSerializer(
            actualizacion, data=request.data
        )
        if serializer.is_valid():
            actualizacion = serializer.save()
            response_serializer = serializers.GetActualizacionSerializer(
                actualizacion, many=False
            )
            return Response(
                data=response_serializer.data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="delete_actualizacion",
        operation_description="""
        Borrar una Actualizacion utilizando su id.

        Sólo se puede borrar si es el creado, el seguimiento está en progreso y no han
        pasado más de 30 minutos desde su creación.
        """,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, actualizacion_pk=None):
        try:
            actualizacion = Actualizacion.objects.get(id=actualizacion_pk)
        except Actualizacion.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            integrante = IntegranteSeguimiento.objects.get(
                seguimiento__exact=actualizacion.seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )
        except IntegranteSeguimiento.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not actualizacion.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se puede borrar una actualización para un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actualizacion.usuario != request.user:
            return Response(
                data={
                    "detail": "No puede borrar una actualización que usted no creó"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actualizacion.fecha_modificacion < datetime.now() - timedelta(
            minutes=30
        ):
            return Response(
                data={
                    "detail": "No se puede borrar una actualización luego de que pasaron 30 minutos desde su última modificación"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actualizacion.delete()

        return Response(
            data={"detail": "La actualización fue borrada correctamente"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_id="create_actualizacion",
        operation_description="""
        Creacion de una Actualización.

        La actualización no puede tener como padre otra actualización que ya tenga padre, es decir,
        sólo se puede llegar a un nivel de respuesta.
        Para poder crear dicha actualización, el usuario debe ser actualmente integrante del
        seguimiento, y no tiene que estar finalizado.
        """,
        request_body=serializers.CreateActualizacionSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request, seguimiento_pk=None):
        try:
            integrante_seguimiento = IntegranteSeguimiento.objects.get(
                seguimiento__id=seguimiento_pk, fecha_hasta__isnull=True
            )
        except IntegranteSeguimiento.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not integrante_seguimiento.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se puede crear una actualización para un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializers.CreateActualizacionSerializer(
            data=request.data, many=False
        )
        if serializer.is_valid():
            padre = serializer.validated_data.get("padre")
            if padre and padre.padre:
                return Response(
                    data={
                        "detail": "No se puede responder a una actualización que ya es respuesta de otra"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            actualizacion = serializer.save(usuario=request.user)
            response_serializer = serializers.GetActualizacionSerializer(
                actualizacion, many=False
            )
            return Response(
                data=response_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_actualizacion = ActualizacionViewSet.as_view({"post": "create"})
list_actualizacion = ActualizacionViewSet.as_view({"get": "list"})
mix_actualizacion = ActualizacionViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)


class ActualizacionAdjuntoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("actualizacion"),
    ]
    OK_EMPTY = {200: serializers.GetActualizacionSerializer}
    OK_CREATED = {201: serializers.GetActualizacionSerializer}

    @swagger_auto_schema(
        operation_id="upload_actualizacion_file",
        operation_description="""
        Subir un archivo adjunto a la actualización.
        
        El archivo no puede tener el mismo nombre que otro anteriormente subido.
        No se pueden subir archivos luego de 30 minutos de la última modificación de la actualización.
        En una actualización no se puede subir más de 3 archivos.
        El tamaño máximo del archivo es de 10MB.
        """,
        request_body=serializers.CreateActualizacionAdjuntoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request, actualizacion_pk=None):
        try:
            actualizacion = Actualizacion.objects.get(pk=actualizacion_pk)
        except Actualizacion.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if actualizacion.usuario != request.user:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            integrante = IntegranteSeguimiento.objects.get(
                seguimiento__exact=actualizacion.seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )
        except IntegranteSeguimiento.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if actualizacion.fecha_modificacion < datetime.now() - timedelta(
            minutes=30
        ):
            return Response(
                data={
                    "detail": "No se puede subir archivos a una actualización luego de que pasaron 30 minutos desde su última modificación"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not actualizacion.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se pueden subir archivos para un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_set = {file.name for file in request.FILES.getlist("file")}

        if len(file_set) != len(request.FILES.getlist("files")):
            return Response(
                data={
                    "detail": "Está subiendo dos archivos con el mismo nombre"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        for file in request.FILES.getlist("files"):
            if default_storage.exists(
                os.path.join(
                    f"/seguimiento_{actualizacion.seguimiento.id}/actualizacion_{actualizacion.id}/{file.name}"
                )
            ):
                return Response(
                    data={
                        "detail": "Ya existe un archivo con el mismo nombre, debe borrar dicho archivo antes de poder subir uno nuevo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if len(file_set) + len(actualizacion.adjuntos.all()) > 3:
            return Response(
                data={
                    "detail": "No se pueden subir más de 3 archivos a una actualización"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                for file in request.FILES.getlist("files"):
                    data = {
                        actualizacion: actualizacion.id,
                        file: file,
                    }
                    serializer = serializers.CreateActualizacionAdjuntoSerializer(
                        data=data
                    )
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        raise Exception

        except Exception as e:
            return Response(
                data={"detail": "Internal error while saving files"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        actualizacion = Actualizacion.objects.get(pk=actualizacion.id)
        serializer = serializers.GetActualizacionSerializer(
            actualizacion, many=False
        )

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="delete_actualizacion_file",
        operation_description="""
        Borrar un archivo adjunto de una actualización.

        El archivo solo puede ser borrado por el que lo subió, y no puede borrarse
        pasado los 30 minutos desde que se subió.
        """,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, file_pk=None):
        try:
            file = ActualizacionAdjunto.objects.get(pk=file_pk)
        except ActualizacionAdjunto.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if file.actualizacion.usuario != request.user:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            integrante = IntegranteSeguimiento.objects.get(
                seguimiento__exact=file.actualizacion.seguimiento,
                usuario__exact=request.user,
                fecha_hasta__isnull=True,
            )
        except IntegranteSeguimiento.DoesNotExist:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if file.fecha_creacion < datetime.now() - timedelta(minutes=30):
            return Response(
                data={
                    "detail": "No se puede borrar archivos de una actualización luego de que pasaron 30 minutos desde su carga"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file.actualizacion.seguimiento.en_progreso:
            return Response(
                data={
                    "detail": "No se pueden subir archivos para un Seguimiento que no se encuentra en progreso"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actualizacion_id = file.actualizacion.id

        file.delete()

        actualizacion = Actualizacion.objects.get(pk=actualizacion_id)
        serializer = serializers.GetActualizacionSerializer(
            actualizacion, many=False
        )

        return Response(data=serializer.data, status=status.HTTP_200_OK)


upload_file = ActualizacionAdjuntoViewSet.as_view({"post": "create"})
delete_file = ActualizacionAdjuntoViewSet.as_view({"delete": "destroy"})

