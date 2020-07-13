from rest_framework import serializers
from curricula import models

# Serializers Carrera


class ViewCarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Carrera
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]


class EditCarreraSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    descripcion = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Carrera
        fields = ["nombre", "descripcion", "color"]


class CreateCarreraSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)
    descripcion = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Carrera
        fields = ["nombre", "descripcion", "color"]
        read_only_fields = ["id", "fecha_creacion"]

    def save(self, institucion):
        carrera = models.Carrera(
            institucion=institucion, **self.validated_data
        )
        carrera.save()
        return carrera
