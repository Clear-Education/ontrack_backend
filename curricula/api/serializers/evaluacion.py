from rest_framework import serializers
from curricula import models
from calificaciones.models import Calificacion
from functools import reduce
from rest_framework.exceptions import ValidationError


class ViewEvaluacionSerializer(serializers.ModelSerializer):
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=models.AnioLectivo.objects.all()
    )

    class Meta:
        model = models.Evaluacion
        fields = [
            "id",
            "nombre",
            "materia",
            "anio_lectivo",
            "fecha_creacion",
            "ponderacion",
        ]


class CreateEvaluacionListSerializer(serializers.ListSerializer):
    def create(self, validated_data):

        anios_lectivos = [e["anio_lectivo"] for e in validated_data]
        materias = [e["materia"] for e in validated_data]
        existing_evaluaciones = models.Evaluacion.objects.filter(
            materia=materias[0], anio_lectivo=anios_lectivos[0]
        )
        if existing_evaluaciones:
            raise ValidationError(
                detail="Ya existen evaluaciones! Modifique las existentes."
            )

        evaluaciones = [models.Evaluacion(**item) for item in validated_data]
        return models.Evaluacion.objects.bulk_create(evaluaciones)

    def update(self, instance, validated_data):
        # Mapping id->existentes and id->nuevos.
        eval_mapping = {e.id: e for e in instance}
        # data_mapping = {item["id"]: item for item in validated_data}
        data_mapping = {0: []}
        for item in validated_data:
            if "id" in item:
                data_mapping[item["id"]] = item
            else:
                data_mapping[0].append(item)
        # Crear y actualizar las evaluaciones existentes.
        ret = []
        for eval_id, data in data_mapping.items():
            e = eval_mapping.get(eval_id, None)
            if e is not None:
                ret.append(self.child.update(e, data))
        for data in data_mapping[0]:
            ret.append(self.child.create(data))

        # Eliminar evaluaciones
        for eval_id, evaluacion in eval_mapping.items():
            if eval_id not in data_mapping:
                if (
                    Calificacion.objects.filter(evaluacion_id=eval_id).count()
                    != 0
                ):
                    raise ValidationError(
                        detail="No se puede eliminar una evaluación que ya contenga calificaciones!"
                    )
                evaluacion.delete()
        return ret

    def validate(self, data):
        """
        Checkear que las FK sean iguales
        """

        anios_lectivos = [e["anio_lectivo"].pk for e in data]
        materias = [e["materia"].pk for e in data]
        if len(set(anios_lectivos)) != 1 or len(set(materias)) != 1:
            raise ValidationError(
                "La materia y anio lectivo deben ser \
                las mismas para todas las evaluaciones"
            )

        ponderaciones = [e["ponderacion"] for e in data]
        if not all(map(lambda x: x > 0, ponderaciones)):
            raise ValidationError("Valores invalidos para ponderacion!")
        total = reduce((lambda x, y: x + y), ponderaciones)
        if total != 1:
            raise ValidationError(detail="Las ponderaciones no suman 1")

        return data


class CreateEvaluacionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=models.AnioLectivo.objects.all(),
        required=True,
        pk_field=serializers.IntegerField(),
    )
    nombre = serializers.CharField(required=False)
    materia = serializers.PrimaryKeyRelatedField(
        queryset=models.Materia.objects.all(),
        required=True,
        pk_field=serializers.IntegerField(),
    )
    ponderacion = serializers.FloatField(required=True)

    class Meta:
        model = models.Evaluacion
        fields = ["id", "anio_lectivo", "nombre", "materia", "ponderacion"]
        list_serializer_class = CreateEvaluacionListSerializer


class DeleteEvaluacionSerializer(serializers.ModelSerializer):
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=models.AnioLectivo.objects.all(),
        required=True,
        pk_field=serializers.IntegerField(),
    )
    materia = serializers.PrimaryKeyRelatedField(
        queryset=models.Materia.objects.all(),
        required=True,
        pk_field=serializers.IntegerField(),
    )

    class Meta:
        model = models.Evaluacion
        fields = ["anio_lectivo", "materia"]
