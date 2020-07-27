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
        request_body=serializers.LoginSerializer, responses={200: serializers.LoginResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        # TODO : Agregar validacion sobre el estado de su institucion
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


@swagger_auto_schema(
    method="get", responses={**responses.STANDARD_ERRORS},
)
@api_view(["GET"])
@pc([IsAuthenticated])
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
            data={"detail": "Successful change of password, please log back in with your new credentials"},
            status=status.HTTP_200_OK,
        )
    else:
        errors = serializer.errors
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("user")]
    serializer_class = serializers.ListUserSerializer
    queryset = User.objects.all()

    OK_CREATE_USER = {201: ""}

    @swagger_auto_schema(
        request_body=serializers.RegistrationSerializer, responses={**OK_CREATE_USER, **responses.STANDARD_ERRORS},
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

    @swagger_auto_schema(responses={200: serializers.ListUserSerializer(many=True), **responses.STANDARD_ERRORS})
    def list(self, request):
        """
        Listar usuarios
        """
        queryset = User.objects.filter(institucion__exact=request.user.institucion).exclude(pk__exact=request.user.pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListUserSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.EditOtherUserSerializer,
        responses={200: serializers.ListUserSerializer(many=False), **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Editar Usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user == request.user:
            serializer = serializers.EditUserSerializer(data=request.data)
            if serializer.is_valid():
                response_user = serializer.update(request.user)
                response_serializer = serializers.ListUserSerializer(response_user, many=False)
                return Response(data=response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if retrieved_user.institucion == request.user.institucion and retrieved_user.is_active:
            permissions = [perm.codename for perm in request.user.groups.permissions.all()]
            if "change_other_user" not in permissions:
                return Response(
                    data={"detail": "Accion prohibida para el rol actual!"}, status=status.HTTP_403_FORBIDDEN
                )
            serializer = serializers.EditOtherUserSerializer(data=request.data)
            if serializer.is_valid():
                response_user = serializer.update(retrieved_user)
                response_serializer = serializers.ListUserSerializer(response_user, many=False)
                return Response(data=response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: "", **responses.STANDARD_ERRORS})
    def destroy(self, request, pk=None):
        """
        Dar de baja a un usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user == request.user:
            retrieved_user.delete()
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        if retrieved_user.institucion != request.user.institucion:
            return Response(data={"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND,)
        retrieved_user.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={202: responses.NotModifiedSerializer, 200: "", **responses.STANDARD_ERRORS})
    @action(detail=False, methods=["PATCH"], name="status")
    def status(self, request, pk=None):
        """
        Cambiar el estado del usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if retrieved_user.institucion != request.user.institucion:
            return Response(data={"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND,)

        serializer = serializers.UserStatusSerializer(data=request.data)

        if serializer.is_valid():
            if retrieved_user.is_active == serializer.validated_data["is_active"]:
                return Response(
                    data={"detail": "El usuario ya se encuentra en el estado solicitado"},
                    status=status.HTTP_202_ACCEPTED,
                )
            if retrieved_user == request.user:
                return Response(
                    data={"detail": "No se puede cambiar el estado del mismo usuario"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.update(retrieved_user, serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: serializers.ListUserSerializer(many=False), **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
        Ver usuario
        """
        retrieved_user = get_object_or_404(User, pk=pk)
        if request.user.institucion == retrieved_user.institucion:
            serializer = serializers.ListUserSerializer(retrieved_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND,)


class GroupViewSet(viewsets.ViewSet):
    """

    Viewset para obtener un grupo y listar grupos

    """

    OK_GET_GROUP = {200: serializers.GroupSerializer()}

    permission_classes = [IsAuthenticated, permission_required("group")]

    @swagger_auto_schema(responses={200: serializers.GroupSerializer(many=True)},)
    def list(self, request):
        """
        Ver una lista de todos los grupos que existen
        """
        queryset = Group.objects.all()
        serializer = serializers.GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={**OK_GET_GROUP, **responses.STANDARD_ERRORS})
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
update_user = UsersViewSet.as_view({"patch": "update", "delete": "destroy", "get": "get"})
status_user = UsersViewSet.as_view({"patch": "status"})

