from rest_framework import serializers
from instituciones.api.serializers import InstitucionSerializer
from curricula.api.serializers import (
    CursoSerializer,
    ViewAnioLectivoSerializer,
)
from alumnos.models import Alumno, AlumnoCurso
from curricula.models import Curso, AnioLectivo
from ontrack import settings
import datetime


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
    curso = CursoSerializer(many=False)
    anio_lectivo = ViewAnioLectivoSerializer(many=False)

    class Meta:
        model = AlumnoCurso
        fields = [
            "id",
            "alumno",
            "curso",
            "anio_lectivo",
        ]

