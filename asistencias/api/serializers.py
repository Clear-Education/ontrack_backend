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
    alumno_curso = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=False, required=True
    )

    class Meta:
        model = Asistencia
        fields = [
            "fecha",
            "asistio",
            "descripcion",
            "alumno_curso",
        ]

    def validate_asistio(self, value):
        if not (0 <= value <= 1):
            raise serializers.ValidationError(
                "El valor del campo asistencia solo puede estar entre 0 y 1"
            )
        return value


class ViewAsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = [
            "id",
            "fecha",
            "asistio",
            "descripcion",
            "alumno_curso",
        ]


class AsistenciaAnioLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaAnioLectivo
        fields = [
            "id",
            "porcentaje",
            "alumno_curso",
        ]

