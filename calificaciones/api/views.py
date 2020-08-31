from rest_framework.viewsets import ModelViewSet
from calificaciones.api import serializers
from curricula.models import Carrera, Curso, Evaluacion, AnioLectivo, Materia
from calificaciones.models import Calificacion
from instituciones.models import Institucion
from alumnos.models import Alumno
from users.permissions import permission_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ontrack import responses
from functools import reduce


class CalificacionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, permission_required("calificacion")]
    queryset = Calificacion.objects.all()
    OK_CREATED = {201: responses.CreatedSerializer}
    OK_CREATED_MULTIPLE = {201: ""}
    OK_EMPTY = {200: ""}
    OK_LIST = {200: serializers.ViewCalficacionSerializer(many=True)}
    OK_VIEW = {200: serializers.ViewCalficacionSerializer()}
    OK_PROMEDIO = {200: serializers.PromedioCalificacionSerializer}
    OK_NOTA_FINAL = {200: serializers.NotaFinalCalificacionSerializer}

    anio_lectivo_param = openapi.Parameter(
        "anio_lectivo",
        openapi.IN_QUERY,
        description="Anio Lectivo para el que queremos listar sus calificaciones",
        type=openapi.TYPE_INTEGER,
    )
    materia_param = openapi.Parameter(
        "materia",
        openapi.IN_QUERY,
        description="Materia para la que queremos listar sus calificaciones",
        type=openapi.TYPE_INTEGER,
    )
    alumno_param = openapi.Parameter(
        "alumno",
        openapi.IN_QUERY,
        description="Alumno para la que queremos listar sus calificaciones",
        type=openapi.TYPE_INTEGER,
    )
    curso_param = openapi.Parameter(
        "curso",
        openapi.IN_QUERY,
        description="Curso para el que queremos listar sus calificaciones",
        type=openapi.TYPE_INTEGER,
    )
    evaluacion_param = openapi.Parameter(
        "evaluacion",
        openapi.IN_QUERY,
        description="Evaluacion para la que queremos listar sus calificaciones",
        type=openapi.TYPE_INTEGER,
    )

    @swagger_auto_schema(
        request_body=serializers.CreateCalificacionSerializer,
        responses={**OK_CREATED, **responses.STANDARD_ERRORS},
    )
    def create(self, request):
        """
        Crea una sola calificacion
        """
        serializer = serializers.CreateCalificacionSerializer(
            data=request.data
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            institucion_alumno = serializer.validated_data[
                "alumno"
            ].institucion_id
            if institucion_alumno != request.user.institucion_id:
                return Response(status=status.HTTP_404_NOT_FOUND)
            alumno_id = serializer.validated_data["alumno"].pk
            evaluacion_id = serializer.validated_data["evaluacion"].pk
            count = Calificacion.objects.filter(
                alumno_id=alumno_id, evaluacion_id=evaluacion_id
            ).count()
            if count == 0:
                calificacion = serializer.create()
                serializer = serializers.ViewCalficacionSerializer(
                    instance=calificacion
                )
            else:
                data = {
                    "detail": "Ya existe una calificacion para ese alumno y evaluacion!"
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.CreateCalificacionListSerializer,
        responses={**OK_CREATED_MULTIPLE, **responses.STANDARD_ERRORS},
    )
    def create_multiple(self, request):
        """
        Crea multiples calificaciones
        """
        serializer = serializers.CreateCalificacionListSerializer(
            data=request.data, context={"request": request}
        )
        data = {}

        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=serializers.EditCalificacionSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def update(self, request, pk=None):
        """
        Edita una instancia unica de calificaciones
        Se pueden editar valores como fecha y puntaje solamente
        """
        calificacion = get_object_or_404(
            Calificacion.objects.filter(
                alumno__institucion_id=request.user.institucion_id
            ),
            pk=pk,
        )
        serializer = serializers.EditCalificacionSerializer(
            data=request.data, partial=True
        )
        data = {}
        if serializer.is_valid(raise_exception=True):
            serializer.update(calificacion, serializer.validated_data)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_EMPTY, **responses.STANDARD_ERRORS},)
    def destroy(self, request, pk=None):
        """
            Borrar una instancia de Calificacion
            Es decir borrar la calificacion que un \
            alumno obtuvo para una evaluacion determinada
        """
        calificacion = get_object_or_404(
            Calificacion.objects.filter(
                alumno__institucion_id=request.user.institucion_id
            ),
            pk=pk,
        )
        calificacion.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=serializers.DeleteManyCalificacionSerializer,
        responses={**OK_EMPTY, **responses.STANDARD_ERRORS},
    )
    def destroy_multiple(self, request, pk=None):
        """
            Borrar todas las calificaciones que corresponden \
            a los alumnos de UN curso y UNA evaluacion (ambos requeridos)
        """
        serializer = serializers.DeleteManyCalificacionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            calificaciones = Calificacion.objects.filter(
                evaluacion_id=serializer.validated_data["evaluacion"].pk,
                alumno__alumnocurso__curso_id=serializer.validated_data[
                    "curso"
                ].pk,
                alumno__alumnocurso__anio_lectivo_id=serializer.validated_data[
                    "evaluacion"
                ].anio_lectivo_id,
            )
            calificaciones.delete()
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={**OK_VIEW, **responses.STANDARD_ERRORS},)
    def get(self, request, pk=None):
        """
            Ver una calificacion especifica
            Ignorar parametros de paginado
        """
        calificacion = get_object_or_404(
            Calificacion.objects.filter(
                alumno__institucion_id=request.user.institucion_id
            ),
            pk=pk,
        )
        s = serializers.ViewCalficacionSerializer(instance=calificacion)
        return Response(data=s.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            anio_lectivo_param,
            materia_param,
            evaluacion_param,
            alumno_param,
            curso_param,
        ],
        responses={**OK_LIST, **responses.STANDARD_ERRORS},
    )
    def list(self, request):
        """
            Busquedas soportadas
                * Por curso y evaluacion: Lista las calificaciones \
                    de los alumnos de un curso para determinada evaluacion
                * Por alumno y anio_lectivo: Lista las calificaciones \
                del alumno para todas las evaluaciones de ese año lectivo
                * Por alumno, materia y anio_lectivo: Lista las calificaciones\
                    que el alumno obtuvo para esa materia en ese año_lectivo
        """
        curso = request.query_params.get("curso", None)
        evaluacion = request.query_params.get("evaluacion", None)
        alumno = request.query_params.get("alumno", None)
        anio_lectivo = request.query_params.get("anio_lectivo", None)
        materia = request.query_params.get("materia", None)

        institucion_id = request.user.institucion_id
        # Filtro base para validar institucion
        queryset = Calificacion.objects.filter(
            alumno__institucion_id=institucion_id
        )

        if curso or evaluacion:
            if curso is None:
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del curso"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif evaluacion is None:
                return Response(
                    data={
                        "detail": "Es necesario especificar el id de la evaluacion"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            curso = get_object_or_404(
                Curso.objects.filter(
                    anio__carrera__institucion_id=institucion_id
                ),
                pk=curso,
            )
            evaluacion = get_object_or_404(
                Evaluacion.objects.filter(
                    anio_lectivo__institucion_id=institucion_id
                ),
                pk=evaluacion,
            )

            queryset = queryset.filter(
                evaluacion_id=evaluacion.pk,
                alumno__alumnocurso__curso_id=curso.pk,
                alumno__alumnocurso__anio_lectivo_id=evaluacion.anio_lectivo_id,
            )
        elif alumno and anio_lectivo:
            if materia:
                # Lista las calificaciones que el alumno \
                # obtuvo para esa materia en ese año_lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                materia = get_object_or_404(
                    Materia.objects.filter(
                        anio__carrera__institucion_id=institucion_id
                    ),
                    pk=materia,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                    evaluacion__materia_id=materia.pk,
                )
            else:
                # Lista las calificaciones \
                # del alumno para todas las evaluaciones de ese año lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                )
        else:
            if alumno:  # Falta anio_lectivo
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del anio_lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:  # Falta alumno
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del alumno"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ViewCalficacionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ViewCalficacionSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[anio_lectivo_param, materia_param, alumno_param],
        responses={**OK_PROMEDIO, **responses.STANDARD_ERRORS},
    )
    def promedio(self, request):
        """
        Consultar el promedio de un alumno en un año lectivo especifico
        - Si se agrega el parámetro materia, solo se responde para esa materia en especifico
        
        * Si paso alumno y anio_lectivo
            Recibo:
                promedios : [ // uno por cada materia que haya cursado en ese año
                    "promedio": Int,
                    "nombre_materia": String
                    ]
                promedio_general : Float
                alumno : Integer
        * Si paso alumno, anio_lectivo Y MATERIA
            Recibo: 
                promedios : [ // lista de UN solo elemento
                    {
                        "promedio": Int,
                        "nombre_materia": String
                    }
                ]
                alumno : Integer

        * Como se calcula el promedio?
            Se suman las notas que se obtuvieron en la materia \
            y se divide por la cantidad 
        """
        alumno = request.query_params.get("alumno", None)
        anio_lectivo = request.query_params.get("anio_lectivo", None)
        materia = request.query_params.get("materia", None)

        institucion_id = request.user.institucion_id
        # Filtro base para validar institucion
        queryset = Calificacion.objects.filter(
            alumno__institucion_id=institucion_id
        )

        data = {"promedios": []}

        if alumno and anio_lectivo:
            if materia:
                # Lista las calificaciones que el alumno \
                # obtuvo para esa materia en ese año_lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                materia = get_object_or_404(
                    Materia.objects.filter(
                        anio__carrera__institucion_id=institucion_id
                    ),
                    pk=materia,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                    evaluacion__materia_id=materia.pk,
                )

                calificaciones = queryset
                total = reduce(
                    lambda x, y: x + y, [c.puntaje for c in calificaciones]
                )
                data["promedios"].append(
                    {
                        "nombre_materia": materia.nombre,
                        "promedio": total / len(calificaciones),
                    }
                )

                data["alumno"] = alumno.pk

            else:
                # Lista las calificaciones \
                # del alumno para todas las evaluaciones de ese año lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                )

                calificaciones = queryset
                materias = [
                    (c.evaluacion.materia_id, c.evaluacion.materia.nombre)
                    for c in calificaciones
                ]
                materias = set(materias)
                overall = 0
                for m_id, m_nombre in materias:

                    c_iter = [
                        c
                        for c in calificaciones
                        if (m_id == c.evaluacion.materia_id)
                    ]

                    total = reduce(
                        lambda x, y: x + y, [c.puntaje for c in c_iter]
                    )
                    data["promedios"].append(
                        {
                            "nombre_materia": m_nombre,
                            "promedio": total / len(c_iter),
                        }
                    )
                    overall += total / len(c_iter)
                data["alumno"] = alumno.pk
                data["promedio_general"] = overall / len(materias)

        else:
            if alumno:  # Falta anio_lectivo
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del anio_lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:  # Falta alumno
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del alumno"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Armar respuesta

        serializer = serializers.PromedioCalificacionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[anio_lectivo_param, materia_param, alumno_param],
        responses={**OK_NOTA_FINAL, **responses.STANDARD_ERRORS},
    )
    def notafinal(self, request):
        """
        Consultar la nota final de un alumno en un año lectivo especifico
        - Si se agrega el parámetro materia, solo se responde para esa materia en especifico

        * Si paso alumno y anio_lectivo
            Recibo:
                notas_finales: // uno por cada materia que haya cursado en ese año
                    ["nota_final": Int,
                    "nombre_materia": String]
                promedio_general : Float
                alumno : Integer

        * Si paso alumno, anio_lectivo Y MATERIA
            Recibo: 
                notas_finales // lista de UN solo elemento
                    "nota_final": Int,
                    "nombre_materia": String
                alumno : Integer
        * Como se calcula el promedio?
            Se multiplican las notas que se obtuvieron en la materia \
            con la ponderación de su correspondiente evaluacion.
        
        * Al comienzo esta "Nota FInal" va a ser muy baja, por lo que solo sirve\
            cuando haya terminado el ciclo lectivo / cursado
        """
        alumno = request.query_params.get("alumno", None)
        anio_lectivo = request.query_params.get("anio_lectivo", None)
        materia = request.query_params.get("materia", None)

        institucion_id = request.user.institucion_id
        # Filtro base para validar institucion
        queryset = Calificacion.objects.filter(
            alumno__institucion_id=institucion_id
        )

        data = {"notas_finales": []}

        if alumno and anio_lectivo:
            if materia:
                # Lista las calificaciones que el alumno \
                # obtuvo para esa materia en ese año_lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                materia = get_object_or_404(
                    Materia.objects.filter(
                        anio__carrera__institucion_id=institucion_id
                    ),
                    pk=materia,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                    evaluacion__materia_id=materia.pk,
                )

                calificaciones = queryset
                # calcular nota final para la materia
                total = map(
                    lambda x: x.puntaje * x.evaluacion.ponderacion,
                    [c for c in calificaciones],
                )
                data["notas_finales"].append(
                    {
                        "nombre_materia": materia.nombre,
                        "nota_final": sum(total),
                    }
                )

                data["alumno"] = alumno.pk

            else:
                # Lista las calificaciones \
                # del alumno para todas las evaluaciones de ese año lectivo
                alumno = get_object_or_404(
                    Alumno.objects.filter(institucion_id=institucion_id),
                    pk=alumno,
                )
                anio_lectivo = get_object_or_404(
                    AnioLectivo.objects.filter(institucion_id=institucion_id),
                    pk=anio_lectivo,
                )
                queryset = queryset.filter(
                    alumno_id=alumno.pk,
                    evaluacion__anio_lectivo_id=anio_lectivo.pk,
                )

                calificaciones = queryset
                materias = [
                    (c.evaluacion.materia_id, c.evaluacion.materia.nombre)
                    for c in calificaciones
                ]
                materias = set(materias)
                overall = 0
                for m_id, m_nombre in materias:
                    # calcular nota final para la materia
                    c_iter = [
                        c
                        for c in calificaciones
                        if (m_id == c.evaluacion.materia_id)
                    ]

                    total = map(
                        lambda x: x.puntaje * x.evaluacion.ponderacion, c_iter
                    )
                    nota_final = sum(total)
                    data["notas_finales"].append(
                        {"nombre_materia": m_nombre, "nota_final": nota_final}
                    )
                    overall += nota_final
                data["alumno"] = alumno.pk
                data["promedio_general"] = overall / len(materias)

        else:
            if alumno:  # Falta anio_lectivo
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del anio_lectivo"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:  # Falta alumno
                return Response(
                    data={
                        "detail": "Es necesario especificar el id del alumno"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Armar respuesta

        serializer = serializers.NotaFinalCalificacionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data, status=status.HTTP_200_OK)


create_calificaciones = CalificacionViewSet.as_view({"post": "create"})
create_calificaciones_multiple = CalificacionViewSet.as_view(
    {"post": "create_multiple", "delete": "destroy_multiple"}
)
view_edit_calificacion = CalificacionViewSet.as_view(
    {"patch": "update", "delete": "destroy", "get": "get"}
)
list_calificaciones = CalificacionViewSet.as_view({"get": "list"})

promedio_calificaciones = CalificacionViewSet.as_view({"get": "promedio"})
notafinal_calificaciones = CalificacionViewSet.as_view({"get": "notafinal"})
