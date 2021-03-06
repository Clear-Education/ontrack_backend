from rest_framework import serializers
from instituciones.api.serializers import InstitucionSerializer
from curricula.api.serializers.anio import CursoSerializerWithCarrera
from curricula.api.serializers.anio_lectivo import ViewAnioLectivoSerializer
from instituciones.models import Institucion
from alumnos.models import Alumno, AlumnoCurso
from curricula.models import Curso, AnioLectivo
from ontrack import settings
import datetime
from calificaciones.models import Calificacion


class CreateAlumnoSerializer(serializers.ModelSerializer):
    dni = serializers.IntegerField(required=True)
    nombre = serializers.CharField(required=True)
    apellido = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    legajo = serializers.CharField(required=False)
    fecha_nacimiento = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )
    direccion = serializers.CharField(required=False)
    localidad = serializers.CharField(required=False)
    provincia = serializers.CharField(required=False)
    fecha_inscripcion = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )

    class Meta:
        model = Alumno
        fields = [
            "dni",
            "nombre",
            "apellido",
            "email",
            "legajo",
            "fecha_nacimiento",
            "direccion",
            "localidad",
            "provincia",
            "fecha_inscripcion",
            "institucion",
        ]


class UpdateAlumnoSerializer(serializers.ModelSerializer):
    dni = serializers.IntegerField(required=False)
    nombre = serializers.CharField(required=False)
    apellido = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    legajo = serializers.CharField(required=False)
    fecha_nacimiento = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )
    direccion = serializers.CharField(required=False)
    localidad = serializers.CharField(required=False)
    provincia = serializers.CharField(required=False)
    fecha_inscripcion = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )

    class Meta:
        model = Alumno
        fields = [
            "dni",
            "nombre",
            "apellido",
            "email",
            "legajo",
            "fecha_nacimiento",
            "direccion",
            "localidad",
            "provincia",
            "fecha_inscripcion",
        ]

    def update(self, alumno):
        alumno.dni = self.validated_data.get("dni", alumno.dni)
        alumno.nombre = self.validated_data.get("nombre", alumno.nombre)
        alumno.apellido = self.validated_data.get("apellido", alumno.apellido)
        alumno.email = self.validated_data.get("email", alumno.email)
        alumno.legajo = self.validated_data.get("legajo", alumno.legajo)
        alumno.fecha_nacimiento = self.validated_data.get(
            "fecha_nacimiento", alumno.fecha_nacimiento
        )
        alumno.direccion = self.validated_data.get(
            "direccion", alumno.direccion
        )
        alumno.localidad = self.validated_data.get(
            "localidad", alumno.localidad
        )
        alumno.provincia = self.validated_data.get(
            "provincia", alumno.provincia
        )
        alumno.fecha_inscripcion = self.validated_data.get(
            "fecha_inscripcion", alumno.fecha_inscripcion
        )
        alumno.save()


class ViewAlumnoSerializer(serializers.ModelSerializer):
    institucion = InstitucionSerializer(many=False)

    class Meta:
        model = Alumno
        fields = [
            "id",
            "dni",
            "nombre",
            "apellido",
            "email",
            "legajo",
            "fecha_nacimiento",
            "direccion",
            "localidad",
            "provincia",
            "fecha_creacion",
            "fecha_inscripcion",
            "institucion",
        ]


class PartialViewAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = [
            "id",
            "dni",
            "nombre",
            "apellido",
            "email",
            "legajo",
        ]


class CreateAlumnoCursoSerializer(serializers.ModelSerializer):
    alumno = serializers.PrimaryKeyRelatedField(
        queryset=Alumno.objects.all(), many=False, required=True
    )
    curso = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(), many=False, required=True
    )
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), many=False, required=True
    )

    class Meta:
        model = AlumnoCurso
        fields = [
            "alumno",
            "curso",
            "anio_lectivo",
        ]


class ViewAlumnoCursoSerializer(serializers.ModelSerializer):
    alumno = ViewAlumnoSerializer(many=False)
    curso = CursoSerializerWithCarrera(many=False)
    anio_lectivo = ViewAnioLectivoSerializer(many=False)

    class Meta:
        model = AlumnoCurso
        fields = [
            "id",
            "alumno",
            "curso",
            "anio_lectivo",
        ]


class ViewAlumnoCursoEvaluacionSerializer(serializers.ModelSerializer):
    alumno = ViewAlumnoSerializer(many=False)
    curso = CursoSerializerWithCarrera(many=False)
    anio_lectivo = ViewAnioLectivoSerializer(many=False)
    puntaje_field = serializers.SerializerMethodField()

    class Meta:
        model = AlumnoCurso
        fields = ["id", "alumno", "curso", "anio_lectivo", "puntaje_field"]

    def get_puntaje_field(self, alumno_curso):
        calificacion = Calificacion.objects.filter(
            evaluacion__id__exact=self.context["evaluacion"],
            alumno__exact=alumno_curso.alumno,
        )
        if calificacion:
            return calificacion[0].puntaje
        return 0


class PartialViewAlumnoCursoSerializer(serializers.ModelSerializer):
    alumno = PartialViewAlumnoSerializer(many=False)
    curso = CursoSerializerWithCarrera(many=False)

    class Meta:
        model = AlumnoCurso
        fields = [
            "id",
            "alumno",
            "curso",
        ]
