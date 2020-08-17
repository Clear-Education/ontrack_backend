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
        queryset=AnioLectivo.objects.all(), many=True
    )

    class Meta:
        model = models.Seguimiento
        fields = [
            "fecha_inicio",
            "descripcion",
            "alumnos",
            "materias",
            "integrantes",
        ]
