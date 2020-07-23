from rest_framework import serializers
from curricula import models


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Curso
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]


class AnioSerializer(serializers.ModelSerializer):
    cursos = CursoSerializer(many=True)
    nombre = serializers.CharField(required=True)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Anio
        fields = ["nombre", "carrera", "color", "cursos"]
        read_only_fields = ["id", "fecha_creacion"]


class CreateCursoSerializer(serializers.ModelSerializer):
    # anio = serializers.PrimaryKeyRelatedField(
    #     queryset=models.Anio.objects.all(),
    # )
    nombre = serializers.CharField(required=True)

    class Meta:
        model = models.Curso
        fields = ["nombre"]

    def create(self):
        # Asumo que ya la carrera seleccionada
        # pertenece a la institucion del usuario
        curso = models.Curso(**self.validated_data)
        curso.save()
        return curso


class EditCursoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)

    class Meta:
        model = models.Curso
        fields = ["nombre"]
        read_only_fields = ["id", "fecha_creacion"]


class CreateAnioSerializer(serializers.ModelSerializer):
    cursos = CreateCursoSerializer(many=True, required=False)
    nombre = serializers.CharField(required=True)
    color = serializers.CharField(required=False)
    carrera = serializers.PrimaryKeyRelatedField(
        queryset=models.Carrera.objects.all(), required=True
    )

    class Meta:
        model = models.Anio
        fields = ["nombre", "carrera", "color", "cursos"]
        read_only_fields = ["id", "fecha_creacion"]

    def create(self):
        # Asumo que ya la carrera seleccionada
        # pertenece a la institucion del usuario
        cursos = self.validated_data.pop("cursos")
        anio = models.Anio(**self.validated_data)
        anio.save()
        if cursos is not None:
            for curso in cursos:
                curso["anio"] = anio
                curso = models.Curso.objects.create(**curso)
                curso.save()
        return anio


class EditAnioSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField()
    color = serializers.CharField()

    class Meta:
        model = models.Anio
        fields = ["nombre", "color"]
        read_only_fields = ["id", "fecha_creacion"]


class ListAnioSerializer(serializers.Serializer):
    carrera = serializers.PrimaryKeyRelatedField(
        required=True, queryset=models.Carrera.objects.all()
    )
