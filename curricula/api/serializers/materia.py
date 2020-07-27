from rest_framework import serializers
from curricula import models


class CreateMateriaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)
    anio = serializers.PrimaryKeyRelatedField(
        queryset=models.Anio.objects.all(), required=True
    )
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "anio", "color"]
        read_only_fields = ["id", "fecha_creacion"]

    def create(self):
        # Asumo que ya el anio seleccionado
        # pertenece a la institucion del usuario
        materia = models.Materia(**self.validated_data)
        materia.save()
        return materia


class EditMateriaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "color"]


class ViewMateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Materia
        fields = "__all__"
