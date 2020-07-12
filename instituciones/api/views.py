from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from instituciones.api.serializers import InstitucionSerializer
from instituciones.models import Institucion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination


class InstitucionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required('institucion')]
    pagination_class = LimitOffsetPagination
    queryset = Institucion.objects.all()
    serializer_class = InstitucionSerializer

    def create(self, request):
        '''
        Crear nueva Institucion
        '''
        serializer = InstitucionSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        '''
        Editar Institucion
        '''
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        serializer = InstitucionSerializer(
            institucion, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            serializer.update(institucion, serializer.validated_data)
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        '''
        Dar de baja una institucion
        '''
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        if institucion.activa:
            institucion.activa = False
            institucion.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], name='alta')
    def alta(self, request, pk=None):
        '''
        Dar de Alta una institucion
        '''
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        if not institucion.activa:
            institucion.activa = True
            institucion.save()
        return Response(status=status.HTTP_200_OK)

    def list(self, request):
        queryset = Institucion.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, pk=None):
        queryset = Institucion.objects.all()
        institucion = get_object_or_404(queryset, pk=pk)
        serializer = InstitucionSerializer(institucion)
        return Response(serializer.data)


create_institucion = InstitucionViewSet.as_view({'post': 'create'})
update_institucion = InstitucionViewSet.as_view({
    'patch': 'update',
    'delete': 'destroy',
    'get': 'get'
    })
alta_institucion = InstitucionViewSet.as_view({'post': 'alta'})
list_institucion = InstitucionViewSet.as_view({'get': 'list'})
