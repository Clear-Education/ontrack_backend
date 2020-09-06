from rest_framework import serializers
from curricula import models


class ListAnioSerializer(serializers.Serializer):
    carrera = serializers.PrimaryKeyRelatedField(
        required=True, queryset=models.Carrera.objects.all()
    )


class BasicAnioSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)

    class Meta:
        model = models.Anio
        fields = ["id", "nombre", "carrera"]


class CursoSerializerWithCarrera(serializers.ModelSerializer):
    anio = BasicAnioSerializer(many=False)

    class Meta:
        model = models.Curso
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]


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
        fields = ["id", "nombre", "carrera", "color", "cursos"]
        read_only_fields = ["fecha_creacion"]


class CreateSingleCursoSerializer(serializers.ModelSerializer):
    # anio = serializers.PrimaryKeyRelatedField(
    #     queryset=models.Anio.objects.all(),
    # )
    nombre = serializers.CharField(required=True)
    anio = serializers.PrimaryKeyRelatedField(
        queryset=models.Anio.objects.all(), required=True
    )

    class Meta:
        model = models.Curso
        fields = ["nombre", "anio"]

    def create(self):
        # Asumo que ya la carrera seleccionada
        # pertenece a la institucion del usuario
        curso = models.Curso(**self.validated_data)
        curso.save()
        return curso


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
        if "cursos" in self.validated_data:
            cursos = self.validated_data.pop("cursos")
        else:
            cursos = None
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

