from rest_framework import serializers
from actualizaciones.models import Actualizacion, ActualizacionAdjunto
from seguimientos.models import Seguimiento
from seguimientos.api.serializers import ListSeguimientoSerializer
from users.models import User


class CreateActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField(required=True)
    padre = serializers.PrimaryKeyRelatedField(
        queryset=Actualizacion.objects.all(), many=False, required=False
    )

    class Meta:
        model = Actualizacion
        fields = [
            "cuerpo",
            "padre",
            "seguimiento",
        ]

    def set_user(self, user):
        self.user = user

    def create(self, validated_data):
        return Actualizacion.objects.create(**validated_data)


class UpdateActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField(required=True)

    class Meta:
        model = Actualizacion
        fields = [
            "cuerpo",
        ]


class GetActualizacionAdjuntoSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        model = ActualizacionAdjunto
        fields = ["id", "fecha_creacion", "file"]


class CreateActualizacionAdjuntoSerializer(serializers.ModelSerializer):
    actualizacion = serializers.PrimaryKeyRelatedField(
        queryset=Actualizacion.objects.all(), many=False
    )
    file = serializers.FileField(max_length=100000, allow_empty_file=False,)

    class Meta:
        model = ActualizacionAdjunto
        fields = [
            "actualizacion",
            "file",
        ]


class GetSimpleActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField()
    seguimiento = serializers.PrimaryKeyRelatedField(
        queryset=Seguimiento.objects.all(), many=False
    )
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False
    )
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    fecha_modificacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    adjuntos = GetActualizacionAdjuntoSerializer(many=True)

    class Meta:
        model = Actualizacion
        fields = [
            "id",
            "cuerpo",
            "seguimiento",
            "usuario",
            "fecha_creacion",
            "fecha_modificacion",
            "adjuntos",
        ]


class GetActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField()
    comentarios = GetSimpleActualizacionSerializer(many=True)
    seguimiento = ListSeguimientoSerializer(many=False)
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False
    )
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    fecha_modificacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    adjuntos = GetActualizacionAdjuntoSerializer(many=True)

    class Meta:
        model = Actualizacion
        fields = [
            "id",
            "cuerpo",
            "comentarios",
            "seguimiento",
            "usuario",
            "fecha_creacion",
            "fecha_modificacion",
            "adjuntos",
        ]

