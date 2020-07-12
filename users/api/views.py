from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from users.api.serializers import RegistrationSerializer, GroupSerializer, ListUserSerializer
from rest_framework import viewsets
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from users.models import User


@api_view(['GET'])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ViewSet):

    permission_classes = [permission_required('user')]

    def create(self, request):
        '''
        Crear nuevos usuarios
        '''
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "Registration Successful"
            data['email'] = user.email
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    # TODO agregar verificación de institución
    def list(self, request):
        '''
        Listar usuarios
        '''
        serializer = ListUserSerializer(User.objects.all(), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ViewSet):
    """

    Viewset para obtener un grupo y listar grupos

    """
    permission_classes = [IsAuthenticated, permission_required('group')]

    # @action(detail=False)
    def list(self, request):
        queryset = Group.objects.all()
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    # @action(detail=True)
    def get(self, request, pk=None):
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, pk=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)


register = UsersViewSet.as_view({'post': 'create'})
list_users = UsersViewSet.as_view({'get': 'list'})
group_list = GroupViewSet.as_view({'get': 'list'})
group_get = GroupViewSet.as_view({'get': 'get'})
