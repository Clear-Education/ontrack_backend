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


class CustomAuthToken(ObtainAuthToken):
    @swagger_auto_schema(
        request_body=serializers.LoginSerializer,
        responses={200: serializers.LoginResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


@swagger_auto_schema(
    method="get", responses={**responses.STANDARD_ERRORS},
)
@api_view(["GET"])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(
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
                "detail": "Cambio de constraseña exitoso, por favor ingresa con tus nuevas credenciales!"
            },
            status=status.HTTP_200_OK,
        )
    else:
        errors = serializer.errors
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, permission_required("user")]
    serializer_class = serializers.ListUserSerializer
    OK_CREATE_USER = {201: ""}
    OK_LIST_USER = {200: serializers.ListUserSerializer(many=True)}
    OK_VIEW_USER = {200: serializers.ListUserSerializer()}

    @swagger_auto_schema(
        request_body=serializers.RegistrationSerializer,
        responses={**OK_CREATE_USER, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear nuevos usuarios
        """
        institucion = request.user.institucion
        serializer = serializers.RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save(institucion)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={**OK_LIST_USER, **responses.STANDARD_ERRORS}
    )
    def list(self, request):
        """
        Listar usuarios
        """
        pagination_class = LimitOffsetPagination
        queryset = User.objects.filter(
            institucion__exact=request.user.institucion
        ).exclude(pk__exact=request.user.pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Editar Usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user == request.user:
            serializer = serializers.EditUserSerializer(data=request.data)
            if serializer.is_valid():
                response_user = serializer.update(request.user)
                response_serializer = serializers.ListUserSerializer(
                    response_user, many=False
                )
                return Response(
                    data=response_serializer.validated_data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        # TODO solo usuarios que estan activos
        if retrieved_user.institucion == request.user.institucion:
            permission_classes = [permission_required("other_user")]

    @swagger_auto_schema(responses={**responses.STANDARD_ERRORS})
    def destroy(self, request, pk=None):
        """
        Dar de baja a un usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if not retrieved_user.is_active:
            return Response(
                data={"detail": "El usuario ya se encuentra inactivo"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if retrieved_user == request.user:
            retrieved_user.is_active = False
            retrieved_user.save()
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        if retrieved_user.institucion != request.user.institucion:
            return Response(
                data={
                    "detail": "No puede borrar un usuario que no pertenece a su institución"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        retrieved_user.is_active = False
        retrieved_user.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], name="alta")
    def alta(self, request, pk=None):
        """
        Volver a reactivar un usuario previamente dado de baja
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user.institucion != request.user.institucion:
            return Response(
                data={
                    "detail": "No puede modificar a un usuario de otra institución"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if retrieved_user.is_active:
            return Response(
                data={"detail": "El usuario ya se encuentra activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        retrieved_user.is_active = True
        retrieved_user.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={**OK_VIEW_USER, **responses.STANDARD_ERRORS}
    )
    def get(self, request, pk=None):
        """
        Ver usuario
        """
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
        responses={200: serializers.GroupSerializer(many=True)},
    )
    def list(self, request):
        """
        Ver una lista de todos los grupos que existen
        """
        queryset = Group.objects.all()
        serializer = serializers.GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={**OK_GET_GROUP, **responses.STANDARD_ERRORS}
    )
    def get(self, request, pk=None):
        """
        Ver un grupo en especial
        """
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
revive_user = UsersViewSet.as_view({"patch": "alta"})

