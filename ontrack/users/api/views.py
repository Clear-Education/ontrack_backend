from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status
from users.api.serializers import RegistrationSerializer, GroupSerializer
from rest_framework import viewsets
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from users.permissions import RoleBasedPermission
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated, RoleBasedPermission])
def user_add(request):
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


@api_view(['GET'])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ViewSet):
    """

    Viewset para obtener un grupo y listar grupos

    """
    permission_classes = [IsAuthenticated]

    @action(detail=False)
    def group_list(self, request):
        queryset = Group.objects.all()
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def group_get(self, request, pk=None):
        queryset = Group.objects.all()
        group = get_object_or_404(queryset, pk=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)


group_list = GroupViewSet.as_view({'get': 'group_list'})
group_get = GroupViewSet.as_view({'get': 'group_get'})
