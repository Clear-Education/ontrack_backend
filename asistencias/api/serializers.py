from rest_framework import serializers
from instituciones.api.serializers import InstitucionSerializer
from curricula.api.serializers.anio import CursoSerializer
from curricula.api.serializers.anio_lectivo import ViewAnioLectivoSerializer
from instituciones.models import Institucion
from alumnos.models import Alumno, AlumnoCurso
from alumnos.api.serializers import ViewAlumnoSerializer
from curricula.models import Curso, AnioLectivo
from asistencias.models import Asistencia, AsistenciaAnioLectivo
from ontrack import settings
import datetime


class CreateAsistenciaSerializer(serializers.ModelSerializer):
    fecha = serializers.DateField(
        required=True, input_formats=settings.DATE_INPUT_FORMAT
    )
    asistio = serializers.FloatField(required=True)
    descripcion = serializers.CharField(required=False)
    alumno = serializers.PrimaryKeyRelatedField(
        queryset=Alumno.objects.all(), many=False, required=True
    )
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), many=False, required=True
    )

    class Meta:
        model = Asistencia
        fields = [
            "fecha",
            "asistio",
            "descripcion",
            "alumno",
            "anio_lectivo",
        ]


class ViewAsistenciaSerializer(serializers.ModelSerializer):
    alumno = ViewAlumnoSerializer(many=False)
    anio_lectivo = ViewAnioLectivoSerializer(many=False)

    class Meta:
        model = Asistencia
        fields = [
            "id",
            "fecha",
            "asistio",
            "descripcion",
            "alumno",
            "anio_lectivo",
        ]


class AsistenciaAnioLectivoSerializer(serializers.ModelSerializer):
    alumno = ViewAlumnoSerializer(many=False)
    anio_lectivo = ViewAnioLectivoSerializer(many=False)

    class Meta:
        model = AsistenciaAnioLectivo
        fields = [
            "id",
            "porcentaje",
            "alumno",
            "anio_lectivo",
        ]

