from rest_framework.viewsets import ModelViewSet
from actualizaciones.api import serializers
from seguimientos.models import Seguimiento, IntegranteSeguimiento
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses
from actualizaciones.models import Actualizacion, ActualizacionAdjunto

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
    def list(self, request, seguimiento_pk):
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
        Modificar un Alumno utilizando su id.
        Se pueden modificar los siguientes campos:
        -  dni (debe estar disponible)
        -  nombre
        -  apellido
        -  email
        -  legajo
        -  fecha_nacimiento
        -  direccion
        -  localidad
        -  provincia
        -  fecha_inscripcion
        """,
        request_body=serializers.UpdateActualizacionSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        pass
        # retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        # institucion = request.user.institucion

        # if retrieved_alumno.institucion != request.user.institucion:
        #     return Response(
        #         data={"detail": "No encontrado."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )

        # serializer = serializers.UpdateAlumnoSerializer(data=request.data)

        # if serializer.is_valid():
        #     if serializer.validated_data.get("dni"):
        #         if retrieved_alumno.dni != serializer.validated_data.get(
        #             "dni"
        #         ):
        #             try:
        #                 Alumno.objects.get(
        #                     dni=serializer.validated_data.get("dni"),
        #                     institucion__exact=institucion,
        #                 ).exclude(pk=pk)
        #                 return Response(
        #                     data={
        #                         "detail": "Alumno con el mismo dni existente"
        #                     },
        #                     status=status.HTTP_400_BAD_REQUEST,
        #                 )
        #             except Alumno.DoesNotExist:
        #                 pass
        #             except:
        #                 return Response(status=status.HTTP_400_BAD_REQUEST)
        #     try:
        #         serializer.update(retrieved_alumno)
        #     except ValidationError as e:
        #         return Response(
        #             data={"detail": e.message},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        #     )

    @swagger_auto_schema(
        operation_id="delete_actualizacion",
        operation_description="Borrar un Alumno utilizando su id.",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        pass
        # retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        # if retrieved_alumno.institucion != request.user.institucion:
        #     return Response(status=status.HTTP_404_NOT_FOUND,)
        # if AlumnoCurso.objects.filter(alumno_id=retrieved_alumno.pk,):
        #     data = {
        #         "detail": "No se puede eliminar un alumno que esté cursando actualmente"
        #     }
        #     return Response(data=data, status=status.HTTP_400_BAD_REQUEST,)

        # retrieved_alumno.delete()
        # return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_actualizacion",
        operation_description="""
        Crear varios Alumnos al mismo tiempo.
        Se debe mandar una lista de objetos, por más que se esté creando sólo un alumno.
        Los alumnos creados no deben tener DNIs iguales entre ellos ni iguales con alumnos ya existentes.
        Se pueden modificar los siguientes campos:
        -  dni (debe estar disponible y es obligatorio)
        -  nombre (obligatorio)
        -  apellido (obligatorio)
        -  email
        -  legajo
        -  fecha_nacimiento
        -  direccion
        -  localidad
        -  provincia
        -  fecha_inscripcion
        """,
        request_body=serializers.CreateActualizacionSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass
        # if type(request.data) is not list:
        #     return Response(
        #         data={"detail": "Debe mandarse una lista de alumnos"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        # institucion = request.user.institucion
        # data = request.data
        # for alumno in data:
        #     alumno["institucion"] = institucion.id
        # serializer = serializers.CreateAlumnoSerializer(
        #     data=request.data, many=True
        # )
        # if serializer.is_valid():
        #     for alumno in serializer.validated_data:
        #         try:
        #             # TODO optimize with a single query
        #             Alumno.objects.get(
        #                 dni=alumno.get("dni"), institucion__exact=institucion
        #             )
        #         except Alumno.DoesNotExist:
        #             continue
        #         except:
        #             return Response(status=status.HTTP_400_BAD_REQUEST)
        #         return Response(
        #             data={"detail": "Alumno con el mismo dni existente"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )

        #     if len(
        #         set([alumno["dni"] for alumno in serializer.validated_data])
        #     ) != len(serializer.validated_data):
        #         return Response(
        #             data={"detail": "Alumnos con el mismo dni en conflicto"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     try:
        #         serializer.save()
        #     except ValidationError as e:
        #         return Response(
        #             data={"detail": e.message},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     ids = {
        #         b.dni: b.id
        #         for b in Alumno.objects.filter(
        #             dni__in=[a.get("dni") for a in serializer.validated_data]
        #         )
        #     }
        #     return Response(data=ids, status=status.HTTP_201_CREATED)
        # else:
        #     data = serializer.errors
        #     return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


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
    OK_EMPTY = {200: ""}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="upload_actualizacion_file",
        operation_description="""
        Crear varios Alumnos al mismo tiempo.
        Se debe mandar una lista de objetos, por más que se esté creando sólo un alumno.
        Los alumnos creados no deben tener DNIs iguales entre ellos ni iguales con alumnos ya existentes.
        Se pueden modificar los siguientes campos:
        -  dni (debe estar disponible y es obligatorio)
        -  nombre (obligatorio)
        -  apellido (obligatorio)
        -  email
        -  legajo
        -  fecha_nacimiento
        -  direccion
        -  localidad
        -  provincia
        -  fecha_inscripcion
        """,
        request_body=serializers.CreateActualizacionAdjuntoSerializer(
            many=True
        ),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        pass

    @swagger_auto_schema(
        operation_id="delete_actualizacion_file",
        operation_description="Borrar un archivo adjunto de una actualizaci'on",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        pass
        # retrieved_alumno = get_object_or_404(Alumno, pk=pk)
        # if retrieved_alumno.institucion != request.user.institucion:
        #     return Response(status=status.HTTP_404_NOT_FOUND,)
        # if AlumnoCurso.objects.filter(alumno_id=retrieved_alumno.pk,):
        #     data = {
        #         "detail": "No se puede eliminar un alumno que esté cursando actualmente"
        #     }
        #     return Response(data=data, status=status.HTTP_400_BAD_REQUEST,)

        # retrieved_alumno.delete()
        # return Response(status=status.HTTP_200_OK)


upload_file = ActualizacionAdjuntoViewSet.as_view(
    {"post": "create", "delete": "destroy"}
)

