from rest_framework import serializers
from seguimientos import models
from curricula.models import Materia, AnioLectivo
from users.models import User
from ontrack import settings
from alumnos.models import AlumnoCurso


class CreateIntegranteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    rol = serializers.PrimaryKeyRelatedField(
        queryset=models.RolSeguimiento.objects.all()
    )
    seguimiento = serializers.PrimaryKeyRelatedField(
        queryset=models.Seguimiento.objects.all()
    )

    class Meta:
        model = models.IntegranteSeguimiento
        fields = ["usuario", "rol", "seguimiento"]


class ListSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "descripcion",
            "en_progreso",
            "fecha_inicio",
            "fecha_cierre",
        ]


class ViewIntegranteSerializer(serializers.ModelSerializer):
    rol = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.IntegranteSeguimiento
        fields = [
            "usuario",
            "rol",
            "fecha_desde",
            "fecha_hasta",
            "fecha_creacion",
            "seguimiento",
        ]


class ViewSeguimientoSerializer(serializers.ModelSerializer):
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), many=True
    )
    integrantes = ViewIntegranteSerializer(many=True)

    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "descripcion",
            "en_progreso",
            "fecha_inicio",
            "fecha_cierre",
            "anio_lectivo",
            "alumnos",
            "integrantes",
            "materias",
        ]


class CreateSeguimientoSerializer(serializers.ModelSerializer):
    fecha_inicio = serializers.DateField(
        required=True, input_formats=settings.DATE_INPUT_FORMAT
    )
    descripcion = serializers.CharField(required=True)
    nombre = serializers.CharField(required=True)
    alumnos = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=True
    )
    materias = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), many=True
    )
    integrantes = CreateIntegranteSerializer(required=True, many=True)
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), required=False
    )

    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "fecha_inicio",
            "descripcion",
            "alumnos",
            "materias",
            "integrantes",
            "anio_lectivo",
        ]


class EditSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seguimiento
        fields = "__all__"


class CreateRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = ["nombre"]


class ViewRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = "__all__"
