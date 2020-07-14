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

    def create(self, institucion):
        carrera = models.Carrera(
            institucion=institucion, **self.validated_data
        )
        carrera.save()
        return carrera


# Serializers Anio + Curso


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


# Serializers Materia + Evaluacion


class CreateEvaluacionSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField()
    ponderacion = serializers.FloatField(required=True)

    class Meta:
        model = models.Evaluacion
        fields = ["nombre", "ponderacion"]


class CreateMateriaSerializer(serializers.ModelSerializer):
    evaluaciones = CreateEvaluacionSerializer(many=True, required=False)
    nombre = serializers.CharField(required=True)
    anio = serializers.PrimaryKeyRelatedField(
        queryset=models.Anio.objects.all(), required=True
    )
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "anio", "color", "evaluaciones"]
        read_only_fields = ["id", "fecha_creacion"]

    def validate_evaluaciones(self, value):
        if value is not None:
            if type(value) is not list:
                raise serializers.ValidationError(
                    "Evaluaciones debe ser una lista"
                )
            pond_list = [x["ponderacion"] for x in value]
            if sum(pond_list) != 1:
                raise serializers.ValidationError(
                    "Las ponderaciones deben sumar 1"
                )
        return value

    def create(self):
        # Asumo que ya el anio seleccionado
        # pertenece a la institucion del usuario
        evaluaciones = self.validated_data.pop("evaluaciones")
        materia = models.Materia(**self.validated_data)
        materia.save()
        if evaluaciones is not None:
            for evaluacion in evaluaciones:
                evaluacion["materia"] = materia
                evaluacion = models.Evaluacion.objects.create(**evaluacion)
                evaluacion.save()
        return materia


class EditEvaluacionSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    ponderacion = serializers.FloatField(required=False)

    class Meta:
        model = models.Evaluacion
        fields = ["nombre", "ponderacion"]


class EditMateriaSerializer(serializers.ModelSerializer):
    evaluaciones = EditEvaluacionSerializer(many=True, required=False)
    nombre = serializers.CharField(required=True)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "color", "evaluaciones"]
        read_only_fields = ["id", "fecha_creacion", "anio"]

    def validate_evaluaciones(self, value):
        if value is not None:
            if type(value) is not list:
                raise serializers.ValidationError(
                    "Evaluaciones debe ser una lista"
                )
            pond_list = [x["ponderacion"] for x in value]
            if sum(pond_list) != 1:
                raise serializers.ValidationError(
                    "Las ponderaciones deben sumar 1"
                )
        return value

    def update(self, instance, validated_data):
        evaluaciones = validated_data.pop("evaluaciones")
        instance.nombre = validated_data.get("nombre", instance.nombre)
        instance.color = validated_data.get("color", instance.color)
        """
        TODO : Actaulizacion a traves de MateriaEvaluacion
        """
        if evaluaciones is not None:

            for evaluacion in evaluaciones:
                curso["anio"] = anio
                curso = models.Curso.objects.create(**curso)
                curso.save()
        anio.save()
        return anio


class EvaluacionSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField()
    ponderacion = serializers.FloatField()

    class Meta:
        model = models.Evaluacion
        fields = ["nombre", "ponderacion"]
        read_only_fields = ["id", "fecha_creacion"]


class MateriaSerializer(serializers.ModelSerializer):
    evaluaciones = EvaluacionSerializer(many=True, required=False)
    nombre = serializers.CharField(required=True)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "anio", "color", "evaluaciones"]
        read_only_fields = ["id", "fecha_creacion"]
