from rest_framework.viewsets import ModelViewSet
from seguimientos.api import serializers
from seguimientos.models import Seguimiento, IntegranteSeguimiento
from seguimientos.models import (
    RolSeguimiento,
    SolicitudSeguimiento,
    EstadoSolicitudSeguimiento,
)
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ValidationError
from drf_yasg import openapi


class SeguimientoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("seguimiento"),
    ]

    serializer_class = serializers.ListSeguimientoSerializer
    queryset = Seguimiento.objects.all()

    OK_LIST = {200: serializers.ListSeguimientoSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewSeguimientoSerializer}
    OK_CREATED = {201: serializers.ViewSeguimientoSerializer}
    OK_EMPTY = {200: ""}

    cerrado_param = openapi.Parameter(
        "cerrado",
        openapi.IN_QUERY,
        description="Incluir seguimientos cerrados o no (booleano)",
        type=openapi.TYPE_BOOLEAN,
    )

    def get_queryset(self, request):
        """
        Restringir la busqueda a Seguimientos Cerrados o no
        """
        queryset = Seguimiento.objects.filter(
            institucion=request.user.institucion,
            integrantes__usuario_id=request.user.pk,
        )
        cerrado = self.request.query_params.get("cerrado", None)
        if cerrado is None or not cerrado:
            queryset = queryset.filter(en_progreso=True)
        return queryset

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
            try:
                s = serializer.create(serializer.validated_data)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        """
        serializer = serializers.EditSeguimientoSerializer(
            data=request.data, context={"request": request}
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            s = get_object_or_404(
                Seguimiento.objects.filter(
                    institucion_id=request.user.institucion_id,
                    en_progreso=True,
                ),
                pk=pk,
            )
            try:
                s = serializer.update(seguimiento=s)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            view_serializer = serializers.ViewSeguimientoSerializer(instance=s)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=view_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.StatusSeguimientoSerializer,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def status(self, request, pk=None):
        """
        Editar el estado del seguimiento
        """
        serializer = serializers.StatusSeguimientoSerializer(
            data=request.data, context={"request": request}
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            s = get_object_or_404(
                Seguimiento.objects.filter(
                    institucion_id=request.user.institucion_id
                ),
                pk=pk,
            )
            s = serializer.update(seguimiento=s)
            view_serializer = serializers.ViewSeguimientoSerializer(instance=s)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=view_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Eliminar un Seguimiento
        """
        seguimiento = get_object_or_404(
            Seguimiento.objects.filter(
                institucion=request.user.institucion,
                integrantes__usuario_id=request.user.pk,
            ),
            pk=pk,
        )
        seguimiento.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[cerrado_param],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
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
        queryset = self.get_queryset(request)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        seguimiento = get_object_or_404(
            Seguimiento.objects.filter(
                institucion=request.user.institucion,
                integrantes__usuario_id=request.user.pk,
            ),
            pk=pk,
        )
        serializer = serializers.ViewSeguimientoSerializer(
            instance=seguimiento
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=serializers.NombreSeguimientoSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def unique(self, request):
        """
        Checkear si el nombre de seguimiento esta en uso
        200 -> Está Disponible
        400 -> No esta disponible o se mando un nombre invalido
        """
        serializer = serializers.NombreSeguimientoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if len(
                Seguimiento.objects.filter(
                    nombre__exact=serializer.data["nombre"].upper(),
                    institucion__exact=request.user.institucion_id,
                )
            ):
                data = {"detail": "El nombre ya esta en uso!"}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class IntegrateSeguimientoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("integranteseguimiento"),
    ]
    queryset = IntegranteSeguimiento.objects.all()
    serializer_class = serializers.CreateIntegranteSerializer
    OK_LIST = {200: serializers.ViewIntegranteSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewIntegranteSerializer}
    OK_CREATED = {201: serializers.ViewIntegranteSerializer}
    OK_EMPTY = {200: ""}

    seguimiento_parameter = openapi.Parameter(
        "seguimiento",
        openapi.IN_PATH,
        description="ID del Seguimiento a consultar",
        type=openapi.TYPE_INTEGER,
        required=True,
    )

    @swagger_auto_schema(
        manual_parameters=[seguimiento_parameter],
        request_body=serializers.EditIntegranteSerializer(many=True),
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def update(self, request, seguimiento=None):
        """
        Editar integrantes de un seguimiento
        """
        serializer = serializers.EditIntegranteSerializer(
            data=request.data, many=True
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            seguimiento = get_object_or_404(
                Seguimiento.objects.filter(
                    institucion=request.user.institucion,
                    integrantes__usuario_id=request.user.pk,
                    en_progreso=True,
                ),
                pk=seguimiento,
            )
            instance = IntegranteSeguimiento.objects.filter(
                seguimiento=seguimiento,
            )
            integrantes = serializer.update(instance, seguimiento=seguimiento)
            r_serializer = serializers.ViewIntegranteSerializer(
                instance=integrantes, many=True
            )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=r_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[seguimiento_parameter],
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, seguimiento=None, pk=None):
        """
        Eliminar un integrante
        """
        integrante = get_object_or_404(
            IntegranteSeguimiento.objects.filter(
                institucion=request.user.institucion,
                integrantes__usuario_id=request.user.pk,
                seguimiento_id=seguimiento,
            ),
            pk=pk,
        )
        integrante.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[seguimiento_parameter],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, seguimiento=None):
        """
        Ignorar parametros de paginacipn!
        No se encuentra paginado!

        List integrantes de seguimiento
        """
        queryset = IntegranteSeguimiento.objects.filter(
            seguimiento__institucion_id=request.user.institucion,
            seguimiento_id=seguimiento,
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[seguimiento_parameter],
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def get(self, request, seguimiento=None, pk=None):
        """
        Ver un integrante de seguimiento
        """
        integrante = get_object_or_404(
            IntegranteSeguimiento.objects.filter(
                institucion=request.user.institucion,
                integrantes__usuario_id=request.user.pk,
                seguimiento_id=seguimiento,
            ),
            pk=pk,
        )
        serializer = serializers.ViewIntegranteSerializer(instance=integrante)
        return Response(serializer.data)


class RolSeguimientoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("rolseguimiento"),
    ]
    queryset = RolSeguimiento.objects.all()
    serializer_class = serializers.ViewRolSerializer
    pagination_class = LimitOffsetPagination
    CREATED_RESPONSE = {201: serializers.CreateRolSerializer}
    OK_LIST = {200: serializers.ViewRolSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewRolSerializer()}

    OK_EMPTY = {200: ""}

    @swagger_auto_schema(
        request_body=serializers.CreateRolSerializer,
        responses={**CREATED_RESPONSE, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear un Rol de Seguimiento
        NO USAR!
        """
        serializer = serializers.CreateRolSerializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
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
        NO USAR!
        """
        queryset = RolSeguimiento.objects.all()
        rol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.CreateRolSerializer(
            rol, data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
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
        NO USAR!
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

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver un Rol de Seguimiento
        """
        queryset = RolSeguimiento.objects.all()
        rol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.ViewRolSerializer(rol)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SolicitudSeguimientoViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        permission_required("solicitudseguimiento"),
    ]
    queryset = SolicitudSeguimiento.objects.all()
    serializer_class = serializers.ViewSolicitudSeguimientoSerializer
    pagination_class = LimitOffsetPagination
    CREATED_RESPONSE = {201: serializers.CreateSolicitudSeguimientoSerializer}
    OK_LIST = {200: serializers.ViewSolicitudSeguimientoSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewSolicitudSeguimientoSerializer()}

    OK_EMPTY = {200: ""}

    @swagger_auto_schema(
        request_body=serializers.CreateSolicitudSeguimientoSerializer,
        responses={**CREATED_RESPONSE, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear una Solicitud de Seguimiento
        """
        serializer = serializers.CreateSolicitudSeguimientoSerializer(
            data=request.data, context={"request": request}
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            sol, f_estado = serializer.save()
            view_serializer = serializers.ViewSolicitudSeguimientoSerializer(
                instance=sol
            )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data=view_serializer.data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        request_body=serializers.EditSolicitudSeguimientosSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar una Solicitud de Seguimiento
        """
        queryset = SolicitudSeguimiento.objects.filter(
            creador__institucion_id=request.user.institucion_id
        )
        sol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.EditSolicitudSeguimientosSerializer(
            instance=sol, data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            sol = serializer.update(sol)
            view_serializer = serializers.ViewSolicitudSeguimientoSerializer(
                instance=sol
            )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=view_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
        Eliminar una Solicitud de Seguimiento
        """
        queryset = SolicitudSeguimiento.objects.filter(
            creador__institucion_id=request.user.institucion_id,
            creador=request.user,
        )
        sol = get_object_or_404(queryset, pk=pk)
        sol.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_LIST, **responses.STANDARD_ERRORS},)
    def list(self, request):
        """
        Listar Solicitudes de Seguimiento
        """
        queryset = SolicitudSeguimiento.objects.filter(
            creador__institucion_id=request.user.institucion_id,
        )
        if request.user.groups.name == "Docente":
            queryset = queryset.filter(creador=request.user,)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver una solicitud de Seguimiento
        """
        queryset = SolicitudSeguimiento.objects.filter(
            creador__institucion_id=request.user.institucion_id,
        )
        sol = get_object_or_404(queryset, pk=pk)
        serializer = serializers.ViewSolicitudSeguimientoSerializer(sol)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.EstadoSolicitudSeguimiento,
        responses={**OK_VIEW, **responses.STANDARD_ERRORS},
    )
    def status(self, request, pk=None):
        """
        Editar el estado de la solicitud de seguimiento
        Estados posibles: "Pendiente", "Aceptada" y "Rechazada"
        Una vez que se llega a rechazada  o aceptada no hay vuelta atrás
        """
        serializer = serializers.EstadoSolicitudSeguimiento(
            data=request.data, context={"request": request}
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            s = get_object_or_404(
                SolicitudSeguimiento.objects.filter(
                    creador__institucion_id=request.user.institucion_id
                ),
                pk=pk,
            )
            estado = EstadoSolicitudSeguimiento.objects.filter(
                nombre=serializer.data["estado"]
            ).first()
            if estado is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            s = serializer.update(solicitud=s, estado=estado)
            view_serializer = serializers.ViewSolicitudSeguimientoSerializer(
                instance=s
            )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=view_serializer.data, status=status.HTTP_200_OK)


# Seguimiento
list_seguimiento = SeguimientoViewSet.as_view({"get": "list"})
status_seguimiento = SeguimientoViewSet.as_view({"patch": "status"})
view_edit_seguimiento = SeguimientoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
create_seguimiento = SeguimientoViewSet.as_view({"post": "create"})
unique_seguimiento = SeguimientoViewSet.as_view({"post": "unique"})

# Integrantes
list_integrantes = IntegrateSeguimientoViewSet.as_view({"get": "list"})
view_delete_integrantes = IntegrateSeguimientoViewSet.as_view(
    {"get": "get", "delete": "destroy"}
)
edit_integrantes = IntegrateSeguimientoViewSet.as_view({"patch": "update"})

# Roles

list_rol = RolSeguimientoViewSet.as_view({"get": "list"})
view_edit_rol = RolSeguimientoViewSet.as_view(
    {"get": "get", "patch": "update", "delete": "destroy"}
)
create_rol = RolSeguimientoViewSet.as_view({"post": "create"})


# Solicitud de Seguimiento

list_solicitudes = SolicitudSeguimientoViewSet.as_view({"get": "list"})
view_edit_delete_solicitudes = SolicitudSeguimientoViewSet.as_view(
    {"get": "get", "delete": "destroy", "patch": "update"}
)
status_solicitud = SolicitudSeguimientoViewSet.as_view({"patch": "status"})
create_solicitudes = SolicitudSeguimientoViewSet.as_view({"post": "create"})
