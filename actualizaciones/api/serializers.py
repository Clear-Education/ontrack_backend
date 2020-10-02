from rest_framework import serializers
from actualizaciones.models import Actualizacion, ActualizacionAdjunto
from seguimientos.models import Seguimiento
from users.models import User


class CreateActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField(required=True)
    padre = serializers.PrimaryKeyRelatedField(
        queryset=Actualizacion.objects.all(), many=False, required=False
    )
    seguimiento = serializers.PrimaryKeyRelatedField(
        queryset=Seguimiento.objects.all(), many=False, required=True
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
    url = serializers.URLField()

    class Meta:
        model = ActualizacionAdjunto
        fields = [
            "id",
            "url",
            "fecha_creacion",
        ]


class CreateActualizacionAdjuntoSerializer(serializers.ModelSerializer):
    actualizacion = serializers.PrimaryKeyRelatedField(
        queryset=Actualizacion.objects.all(), many=False
    )
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    url = serializers.URLField()

    class Meta:
        model = ActualizacionAdjunto
        fields = [
            "actualizacion",
            "url",
            "fecha_creacion",
        ]


class GetActualizacionSerializer(serializers.ModelSerializer):
    cuerpo = serializers.CharField()
    padre = serializers.PrimaryKeyRelatedField(
        queryset=Actualizacion.objects.all(), many=False
    )
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
            "padre",
            "seguimiento",
            "usuario",
            "fecha_creacion",
            "fecha_modificacion",
            "adjuntos",
        ]

