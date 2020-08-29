from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    action,
    permission_classes as pc,
)
from rest_framework import status
from users.api import serializers
from rest_framework import viewsets
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from users.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from django.core.exceptions import ValidationError


class CustomAuthToken(ObtainAuthToken):
    @swagger_auto_schema(
        operation_id="login",
        operation_description="""
        Ingreso al sistema a través de credenciales (email y contraseña).
        Devuelve un token que debe ser utilizado en todas las llamadas a la API para identificarse.
        También devuelve la entidad usuario
        """,
        request_body=serializers.LoginSerializer,
        responses={200: serializers.LoginResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user = User.objects.get(pk=user.pk)
        if not user.is_superuser and not user.institucion.activa:
            return Response(status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        user.token = token.key
        response_serializer = serializers.LoginResponseSerializer(user)
        return Response(data=response_serializer.data)


@swagger_auto_schema(
    operation_id="logout",
    operation_description="""
    Desautenticarse en el sistema.
    """,
    method="get",
    responses={**responses.STANDARD_ERRORS},
)
@api_view(["GET"])
@pc([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(
    operation_id="change_password",
    operation_description="""
    Cambiar la contraseña de un usuario.
    Se debe ingresar la contraseña actual y la nueva contraseña repetida por seguridad.
    """,
    method="patch",
    request_body=serializers.ChangePasswordSerializer,
    responses={200: responses.SuccessDetailSerializer},
)
@api_view(["PATCH"])
@pc([IsAuthenticated])
def change_password(request):
    serializer = serializers.ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(request.user)
        request.user.auth_token.delete()
        return Response(
            data={
                "detail": "Successful change of password, please log back in with your new credentials"
            },
            status=status.HTTP_200_OK,
        )
    else:
        errors = serializer.errors
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("user")]
    OK_CREATE_USER = {201: ""}

    @swagger_auto_schema(
        operation_id="create_usuario",
        operation_description="""
        Creación de un nuevo usuario
        Se debe pasar obligatoriamente el email, la contraseña (repetida por seguridad) y el grupo (id del grupo o "tipo de cuenta").
        El mail no puede estar repetido con ningún otro usuario.
        """,
        request_body=serializers.RegistrationSerializer,
        responses={**OK_CREATE_USER, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        institucion = request.user.institucion
        serializer = serializers.RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            try:
                serializer.save(institucion)
            except ValidationError as e:
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id="list_usuarios",
        operation_description="Listar usuarios de la institución.",
        responses={
            200: serializers.ListUserSerializer(many=True),
            **responses.STANDARD_ERRORS,
        },
    )
    def list(self, request):
        queryset = User.objects.filter(
            institucion__exact=request.user.institucion
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListUserSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="update_usuario",
        operation_description="""
        Modificar un Usuario utilizando su id.
        En este endpoint se puede modificar el propio usuario que se encuentra logueado u otro de la institución (si se tiene permisos).
        Los campos a ingresar son:
        -  email
        -  name
        -  phone
        -  date_of_birth
        -  picture
        -  dni
        -  last_name
        -  cargo
        -  legajo
        -  direccion
        -  localidad
        -  provincia
        -  groups (solo en el caso de editar otro usuario)
        """,
        request_body=serializers.EditOtherUserSerializer,
        responses={
            200: serializers.ListUserSerializer(many=False),
            **responses.STANDARD_ERRORS,
        },
    )
    def update(self, request, pk=None):
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user == request.user:
            serializer = serializers.EditUserSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    response_user = serializer.update(request.user)
                except ValidationError as e:
                    return Response(
                        data={"detail": e.message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                response_serializer = serializers.ListUserSerializer(
                    response_user, many=False
                )
                return Response(
                    data=response_serializer.data, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        if retrieved_user.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if retrieved_user.is_active:
            permissions = [
                perm.codename for perm in request.user.groups.permissions.all()
            ]
            if "change_other_user" not in permissions:
                return Response(
                    data={"detail": "Accion prohibida para el rol actual!"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = serializers.EditOtherUserSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    response_user = serializer.update(retrieved_user)
                except ValidationError as e:
                    return Response(
                        data={"detail": e.message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                response_serializer = serializers.ListUserSerializer(
                    response_user, many=False
                )
                return Response(
                    data=response_serializer.data, status=status.HTTP_200_OK
                )

            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                data={"detail": "El usuario a editar no está activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_id="delete_usuario",
        operation_description="Borrar un Usuario utilizando su id.",
        responses={200: "", **responses.STANDARD_ERRORS},
    )
    def destroy(self, request, pk=None):
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user == request.user:
            retrieved_user.delete()
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        if retrieved_user.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        retrieved_user.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="change_status_usuario",
        operation_description="""
        Modificar el estado de un Usuario utilizando su id.
        En este endpoint se permite dar de baja al usuario o volverlo a dar de alta.
        Esto se realiza con el campo is_activo que recibe un booleano que indica el estado en el que se deséa que quede el usuario
        El usuario dado de baja lógicamente, ya no podrá interactuar con el sistema.
        """,
        request_body=serializers.UserStatusSerializer,
        responses={
            202: responses.NotModifiedSerializer,
            200: "",
            **responses.STANDARD_ERRORS,
        },
    )
    @action(detail=False, methods=["PATCH"], name="status")
    def status(self, request, pk=None):
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user.institucion != request.user.institucion:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = serializers.UserStatusSerializer(data=request.data)

        if serializer.is_valid():
            if (
                retrieved_user.is_active
                == serializer.validated_data["is_active"]
            ):
                return Response(
                    data={
                        "detail": "El usuario ya se encuentra en el estado solicitado"
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            if retrieved_user == request.user:
                return Response(
                    data={
                        "detail": "No se puede cambiar el estado del mismo usuario"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.update(retrieved_user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_id="get_usuario",
        operation_description="""
        Obtener un Usuario utilizando su id.

        Se deben ignorar los parámetros limit y offset, ya que no aplican a este endpoint.
        """,
        responses={
            200: serializers.ListUserSerializer(many=False),
            **responses.STANDARD_ERRORS,
        },
    )
    def get(self, request, pk=None):
        retrieved_user = get_object_or_404(User, pk=pk)
        if request.user.institucion == retrieved_user.institucion:
            serializer = serializers.ListUserSerializer(retrieved_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"detail": "No encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GroupViewSet(viewsets.ViewSet):
    """

    Viewset para obtener un grupo y listar grupos

    """

    OK_GET_GROUP = {200: serializers.GroupSerializer()}

    permission_classes = [IsAuthenticated, permission_required("group")]

    @swagger_auto_schema(
        operation_id="list_grupo",
        operation_description='Listar los grupos o "Tipo de Cuenta" existentes.',
        responses={200: serializers.GroupSerializer(many=True)},
    )
    def list(self, request):
        queryset = Group.objects.all()
        serializer = serializers.GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id="get_grupo",
        operation_description='Obtener un Grupo o "Tipo de Cuenta" utilizando su id.',
        responses={**OK_GET_GROUP, **responses.STANDARD_ERRORS},
    )
    def get(self, request, pk=None):
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, pk=pk)
        serializer = serializers.GroupSerializer(group)
        return Response(serializer.data)


register = UsersViewSet.as_view({"post": "create"})
list_users = UsersViewSet.as_view({"get": "list"})
group_list = GroupViewSet.as_view({"get": "list"})
group_get = GroupViewSet.as_view({"get": "get"})
login = CustomAuthToken.as_view()
update_user = UsersViewSet.as_view(
    {"patch": "update", "delete": "destroy", "get": "get"}
)

status_user = UsersViewSet.as_view({"patch": "status"})

