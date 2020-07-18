from rest_framework import serializers
from curricula import models
from instituciones.api.serializers import InstitucionSerializer
from ontrack import settings
import datetime

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
        carrera = models.Carrera(institucion=institucion, **self.validated_data)
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
    carrera = serializers.PrimaryKeyRelatedField(queryset=models.Carrera.objects.all(), required=True)

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
    carrera = serializers.PrimaryKeyRelatedField(required=True, queryset=models.Carrera.objects.all())


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
    anio = serializers.PrimaryKeyRelatedField(queryset=models.Anio.objects.all(), required=True)
    color = serializers.CharField(required=False)

    class Meta:
        model = models.Materia
        fields = ["nombre", "anio", "color", "evaluaciones"]
        read_only_fields = ["id", "fecha_creacion"]

    def validate_evaluaciones(self, value):
        if value is not None:
            if type(value) is not list:
                raise serializers.ValidationError("Evaluaciones debe ser una lista")
            pond_list = [x["ponderacion"] for x in value]
            if sum(pond_list) != 1:
                raise serializers.ValidationError("Las ponderaciones deben sumar 1")
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
                raise serializers.ValidationError("Evaluaciones debe ser una lista")
            pond_list = [x["ponderacion"] for x in value]
            if sum(pond_list) != 1:
                raise serializers.ValidationError("Las ponderaciones deben sumar 1")
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


class AnioLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnioLectivo
        fields = ["nombre", "fecha_desde", "fecha_hasta"]
        extra_kwargs = {
            "nombre": {"required": True},
            "fecha_desde": {"required": True, "input_formats": settings.DATE_INPUT_FORMAT},
            "fecha_hasta": {"required": True, "input_formats": settings.DATE_INPUT_FORMAT},
        }
        read_only_fields = ["id", "fecha_creacion"]

    def validate(self, data):
        if data["fecha_desde"] >= data["fecha_hasta"]:
            raise serializers.ValidationError("La fecha de inicio del Año Lectivo debe ser menor a la fecha fin")
        return data

    def create(self, institucion):
        anio_lectivo = models.AnioLectivo(**self.validated_data)
        anio_lectivo.institucion = institucion
        anio_lectivo.save()


class EditAnioLectivoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    fecha_desde = serializers.DateField(required=False, input_formats=settings.DATE_INPUT_FORMAT)
    fecha_hasta = serializers.DateField(required=False, input_formats=settings.DATE_INPUT_FORMAT)

    class Meta:
        model = models.AnioLectivo
        fields = ["nombre", "fecha_desde", "fecha_hasta"]

    def get_existing_anio_lectivo(self, anio_lectivo):
        self.anio_lectivo = anio_lectivo

    def validate(self, data):
        fecha_desde_temp = data.get("fecha_desde", self.anio_lectivo.fecha_desde)
        fecha_hasta_temp = data.get("fecha_hasta", self.anio_lectivo.fecha_hasta)
        if fecha_desde_temp >= fecha_hasta_temp:
            raise serializers.ValidationError(
                {"detail": "La fecha de inicio del Año Lectivo debe ser menor a la fecha fin"}
            )
        if data.get("fecha_desde", None) is not None or data.get("fecha_hasta", None) is not None:
            if datetime.date.today() > self.anio_lectivo.fecha_desde:
                raise serializers.ValidationError("No se puede modificar el Año Lectivo luego de que ya comenzó")
        return data

    def update(self, instance):
        instance.nombre = self.validated_data.get("nombre", instance.nombre)
        instance.fecha_desde = self.validated_data.get("fecha_desde", instance.fecha_desde)
        instance.nombre = self.validated_data.get("fecha_hasta", instance.fecha_hasta)
        instance.save()


class ViewAnioLectivoSerializer(serializers.ModelSerializer):
    institucion = InstitucionSerializer(many=False)

    class Meta:
        model = models.AnioLectivo
        fields = ["id", "nombre", "fecha_desde", "fecha_hasta", "institucion"]
