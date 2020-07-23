from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import anio_lectivo as serializers
from curricula.models import AnioLectivo
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses


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
        anio_lectivo_list = AnioLectivo.objects.filter(
            institucion__exact=request.user.institucion
        )
        serializer = serializers.ViewAnioLectivoSerializer(
            anio_lectivo_list, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
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
            serializer.update(anio_lectivo)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        anio_lectivo = get_object_or_404(AnioLectivo, pk=pk)
        if anio_lectivo.institucion != request.user.institucion:
            return Response(status=status.HTTP_404_NOT_FOUND)
        anio_lectivo.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.AnioLectivoSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        serializer = serializers.AnioLectivoSerializer(data=request.data)
        if serializer.is_valid():
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
            serializer.create(request.user.institucion)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


create_anio_lectivo = AnioLectivoViewSet.as_view({"post": "create"})
list_anio_lectivo = AnioLectivoViewSet.as_view({"get": "list"})
update_anio_lectivo = AnioLectivoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
