from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import anio_lectivo as serializers
from curricula.models import AnioLectivo
from alumnos.models import AlumnoCurso
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from django.core.exceptions import ValidationError
import datetime


class AnioLectivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("aniolectivo")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewAnioLectivoSerializer()}
    OK_LIST = {200: serializers.ViewAnioLectivoSerializer(many=True)}
    OK_CREATED = {201: ""}

    @swagger_auto_schema(
        operation_id="get_anio_lectivo",
        operation_description="""
        Obtener un Año Lectivo utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ViewAnioLectivoSerializer(anio_lectivo)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="get_anio_lectivo_actual",
        operation_description="""
        Obtener el año lectivo que transcurre actualmente

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def actual(self, request):
        hoy = datetime.date.today()

        current = AnioLectivo.objects.filter(
            institucion=request.user.institucion,
            fecha_hasta__gte=hoy,
            fecha_desde__lte=hoy,
        ).first()
        if current:
            serializer = serializers.ViewAnioLectivoSerializer(current)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="list_anio_lectivo",
        operation_description="""
        Listar las asistencia de una institucion.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        anio_lectivo_list = AnioLectivo.objects.filter(
            institucion__exact=request.user.institucion
        )
        serializer = serializers.ViewAnioLectivoSerializer(
            anio_lectivo_list, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_anio_lectivo",
        operation_description="""
        Modificar un Año Lectivo utilizando su id.
        Sólo se puede modificar el nombre, su fecha_desde y fecha_hasta, siempre y cuando la fecha desde venga después de la fecha hasta, 
        y no interfiera con otros Años Lectivos de la institucion (no pueden estar superpuestos por fechas).
        Tampoco puede ser modificado si en su rango de fechas actual, el año lectivo ya comenzó o pasó completamente.
        """,
        request_body=serializers.EditAnioLectivoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.EditAnioLectivoSerializer(data=request.data)
        serializer.get_existing_anio_lectivo(anio_lectivo)
        if serializer.is_valid():
            updated_anio_lectivo = {
                "nombre": serializer.validated_data.get(
                    "nombre", anio_lectivo.nombre
                ),
                "fecha_desde": serializer.validated_data.get(
                    "fecha_desde", anio_lectivo.fecha_desde
                ),
                "fecha_hasta": serializer.validated_data.get(
                    "fecha_hasta", anio_lectivo.fecha_hasta
                ),
            }
            for institucion_retrieved in AnioLectivo.objects.filter(
                institucion__exact=request.user.institucion
            ).exclude(id__exact=anio_lectivo.id):
                if (
                    (
                        institucion_retrieved.fecha_desde
                        <= updated_anio_lectivo["fecha_desde"]
                        and institucion_retrieved.fecha_hasta
                        >= updated_anio_lectivo["fecha_desde"]
                    )
                    or (
                        institucion_retrieved.fecha_desde
                        <= updated_anio_lectivo["fecha_hasta"]
                        and institucion_retrieved.fecha_hasta
                        >= updated_anio_lectivo["fecha_hasta"]
                    )
                    or (
                        updated_anio_lectivo["fecha_desde"]
                        <= institucion_retrieved.fecha_desde
                        and updated_anio_lectivo["fecha_hasta"]
                        >= institucion_retrieved.fecha_hasta
                    )
                ):
                    return Response(
                        data={
                            "detail": "Las fechas entran en conflicto con el Año Lectivo de nombre "
                            + institucion_retrieved.nombre
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            try:
                serializer.update(anio_lectivo)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="delete_anio_lectivo",
        operation_description="Borrar un Año Lectivo utilizando su id.",
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # TODO : Agregar checkeo con seguimiento
        if AlumnoCurso.objects.filter(anio_lectivo=anio_lectivo).count() != 0:
            data = {
                "detail": "No se puede eliminar un Año Lectivo que haya tenido alumnos cursando!"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        anio_lectivo.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="create_anio_lectivo",
        operation_description="""
        Crear un Año Lectivo.
        Los campos a ingresar son: nombre, fecha_desde y fecha_hasta. Todos son obligatorios.
        No se pueden crear dos Años Lectivos con el mismo nombre, ni con fechas superpuestas.
        """,
        request_body=serializers.AnioLectivoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.AnioLectivoSerializer(data=request.data)
        if serializer.is_valid():
            if AnioLectivo.objects.filter(
                institucion__exact=request.user.institucion,
                nombre__exact=serializer.validated_data["nombre"],
            ):
                return Response(
                    data={
                        "detail": "No se pueden crear Años Lectivos con el mismo nombre"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for institucion_retrieved in AnioLectivo.objects.filter(
                institucion__exact=request.user.institucion
            ):
                if (
                    (
                        institucion_retrieved.fecha_desde
                        <= serializer.validated_data["fecha_desde"]
                        and institucion_retrieved.fecha_hasta
                        >= serializer.validated_data["fecha_desde"]
                    )
                    or (
                        institucion_retrieved.fecha_desde
                        <= serializer.validated_data["fecha_hasta"]
                        and institucion_retrieved.fecha_hasta
                        >= serializer.validated_data["fecha_hasta"]
                    )
                    or (
                        serializer.validated_data["fecha_desde"]
                        <= institucion_retrieved.fecha_desde
                        and serializer.validated_data["fecha_hasta"]
                        >= institucion_retrieved.fecha_hasta
                    )
                ):
                    return Response(
                        data={
                            "detail": "Las fechas entran en conflicto con el Año Lectivo de nombre "
                            + institucion_retrieved.nombre
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            try:
                serializer.create(request.user.institucion)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_anio_lectivo = AnioLectivoViewSet.as_view({"post": "create"})
list_anio_lectivo = AnioLectivoViewSet.as_view({"get": "list"})
actual_anio_lectivo = AnioLectivoViewSet.as_view({"get": "actual"})

update_anio_lectivo = AnioLectivoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
