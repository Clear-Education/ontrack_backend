from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from users.api import serializers
from rest_framework import viewsets
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from users.models import User
from rest_framework.authtoken.views import ObtainAuthToken
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


@api_view(["GET"])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, permission_required("user")]
    OK_CREATE_USER = {201: ""}

    @swagger_auto_schema(
        request_body=serializers.RegistrationSerializer,
        response={**OK_CREATE_USER, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear nuevos usuarios
        """
        serializer = serializers.RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    # TODO agregar verificación de institución
    @swagger_auto_schema(
        responses={200: serializers.UserSerializer(many=True)},
    )
    def list(self, request):
        """
        Listar usuarios
        """
        serializer = serializers.ListUserSerializer(
            User.objects.all(), many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)


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
