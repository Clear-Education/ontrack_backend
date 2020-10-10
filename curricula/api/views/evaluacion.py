from rest_framework.viewsets import ModelViewSet
from curricula.api.serializers import evaluacion as serializers
from curricula.models import Evaluacion, Materia, AnioLectivo
from calificaciones.models import Calificacion
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, get_list_or_404
from drf_yasg.utils import swagger_auto_schema
from ontrack import responses
from drf_yasg import openapi
from django.core.exceptions import ValidationError


class EvaluacionViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated, permission_required("evaluacion")]
    OK_EMPTY = {200: ""}
    OK_VIEW = {200: serializers.ViewEvaluacionSerializer()}
    OK_LIST = {200: serializers.ViewEvaluacionSerializer(many=True)}
    OK_CREATED = {201: responses.CreatedSerializer}
    anio_lectivo_param = openapi.Parameter(
        "anio_lectivo",
        openapi.IN_QUERY,
        description="Anio Lectivo para el que queremos listar sus Evaluaciones",
        type=openapi.TYPE_INTEGER,
    )
    materia_param = openapi.Parameter(
        "materia",
        openapi.IN_QUERY,
        description="Materia para la que queremos listar sus evaluaciones",
        type=openapi.TYPE_INTEGER,
    )

    def get_queryset(self, institucion):
        """
        Restringir la busqueda de Materias por un año
        """
        queryset = Evaluacion.objects.filter(
            materia__anio__carrera__institucion=institucion
        )
        anio_lectivo = self.request.query_params.get("anio_lectivo", None)
        if anio_lectivo is not None:
            queryset = queryset.filter(anio_lectivo=anio_lectivo,)
        return queryset

    @swagger_auto_schema(
        responses={**OK_VIEW, **responses.STANDARD_ERRORS}, tags=["evaluacion"]
    )
    def get(self, request, pk=None):
        """
        Ver una evaluacion
        """
        # Busca el objeto por clave primaria, si falla 404
        evaluacion = get_object_or_404(
            self.get_queryset(request.user.institucion), pk=pk
        )
        # Serializa para poder devolver los datos
        serializer = serializers.ViewEvaluacionSerializer(evaluacion)
        # Devuelve el resultado
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[anio_lectivo_param],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request, materia_id=None):
        """
        Listar las materias de la institucion del usuario logeado
        """
        # Busca la materia, sino 404 (debe ser de su institucion)
        get_object_or_404(
            Materia.objects.filter(
                anio__carrera__institucion_id=request.user.institucion.id,
            ),
            pk=materia_id,
        )
        # Busca el filtro que le permite ejecutar la busqueda
        evaluacion_list = self.get_queryset(request.user.institucion)
        # Ejecuta la busqueda de evaluaciones
        evaluacion_list = evaluacion_list.filter(materia_id=materia_id)
        # Procesa el resultado para devolver
        serializer = serializers.ViewEvaluacionSerializer(
            evaluacion_list, many=True
        )
        # Responde con resultados
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.CreateEvaluacionSerializer(many=True),
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crear evaluaciones
        """
        serializer = serializers.CreateEvaluacionSerializer(
            data=request.data, many=True
        )
        data = {}
        # Valida los datos con el serializador de crear evaluacion
        if serializer.is_valid(raise_exception=True):
            # Valida que la materia sea de la institucion
            get_object_or_404(
                Materia.objects.filter(
                    anio__carrera__institucion_id=request.user.institucion.id,
                ),
                pk=serializer.validated_data[0]["materia"].pk,
            )
            # Valida que el año lectivo sea de la institucion
            get_object_or_404(
                AnioLectivo.objects.filter(
                    institucion_id=request.user.institucion.id,
                ),
                pk=serializer.validated_data[0]["anio_lectivo"].pk,
            )
            try:
                # Crea las evaluaciones
                serializer.create(serializer.validated_data)
            except ValidationError as e:
                # Si existió un error responde con un BAD REQUEST
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Si fallaron las primeras validaciones devuelve 404
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.CreateEvaluacionSerializer(many=True),
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request):
        """
        Actualizar evaluaciones
        """
        serializer = serializers.CreateEvaluacionSerializer(
            data=request.data, many=True
        )
        data = {}
        # Valida datos ingresados
        if serializer.is_valid(raise_exception=True):
            # Busca las evaluaciones existentes a editar
            instance = Evaluacion.objects.filter(
                materia=serializer.validated_data[0]["materia"].pk,
                anio_lectivo=serializer.validated_data[0]["anio_lectivo"].pk,
            )
            try:
                # Actualiza pasando instancias actuales y datos recibidos
                serializer.update(instance, serializer.validated_data)
            except ValidationError as e:
                # Si hubieron errores entonces 400
                return Response(
                    data={"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Si no era válido entonces 400
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.DeleteEvaluacionSerializer(),
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy(self, request):
        """
        Eliminar todas las evaluaciones de una Materia y un dado Año lectivo
        """
        serializer = serializers.DeleteEvaluacionSerializer(data=request.data)
        data = {}
        # Valida datos ingresados
        if serializer.is_valid(raise_exception=True):
            # Busca instancias a eliminar
            instances = Evaluacion.objects.filter(
                materia=serializer.validated_data["materia"].pk,
                anio_lectivo=serializer.validated_data["anio_lectivo"].pk,
            )
            if not instances:
                # Si no hay instancias no pasa nada
                Response(status=status.HTTP_200_OK)
            for e in instances:
                # Checkea que cada instancia no tenga calificaciones
                if Calificacion.objects.filter(evaluacion=e).count() != 0:
                    # Si tiene calificaciones no se puede borrar
                    # se perderían datos
                    data = {
                        "detail": "No se puede eliminar una evaluación que \
                            ya contenga calificaciones!"
                    }
                    return Response(
                        data=data, status=status.HTTP_400_BAD_REQUEST
                    )
            # Si todo OK, borra las evaluaciones
            instances.delete()
        else:
            # Si hubieron errores de validación 400
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


view_evaluacion = EvaluacionViewSet.as_view({"get": "get"})
list_evaluacion = EvaluacionViewSet.as_view({"get": "list"})
create_evaluacion = EvaluacionViewSet.as_view(
    {"post": "create", "put": "update", "delete": "destroy"}
)
