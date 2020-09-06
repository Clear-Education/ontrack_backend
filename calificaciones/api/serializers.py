from rest_framework import serializers
from calificaciones import models
from curricula.models import Evaluacion, Curso
from calificaciones.models import Calificacion
from alumnos.models import Alumno, AlumnoCurso
from ontrack import settings
from django.shortcuts import get_object_or_404
from alumnos.api.serializers import ViewAlumnoSerializer


class ViewCalficacionSerializer(serializers.ModelSerializer):
    alumno = ViewAlumnoSerializer()

    class Meta:
        model = models.Calificacion
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]


class CreateCalificacionSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(required=False)
    fecha = serializers.DateField(required=True)
    puntaje = serializers.FloatField(required=True, max_value=10, min_value=0)

    alumno = serializers.PrimaryKeyRelatedField(
        queryset=Alumno.objects.all(), required=True
    )
    evaluacion = serializers.PrimaryKeyRelatedField(
        queryset=Evaluacion.objects.all(), required=True
    )

    class Meta:
        model = models.Calificacion
        fields = ["fecha", "puntaje", "alumno", "evaluacion"]
        extra_kwargs = {"fecha": {"input_formats": settings.DATE_INPUT_FORMAT}}

    def create(self):
        calificacion = models.Calificacion(**self.validated_data)
        calificacion.save()
        return calificacion


class CalificacionSerializer(serializers.Serializer):

    puntaje = serializers.FloatField(required=True, min_value=0, max_value=10)
    alumno = serializers.PrimaryKeyRelatedField(
        queryset=Alumno.objects.all(), required=True
    )


class CreateCalificacionListSerializer(serializers.ModelSerializer):

    # id = serializers.IntegerField(required=False)
    fecha = serializers.DateField(required=True)
    evaluacion = serializers.PrimaryKeyRelatedField(
        queryset=Evaluacion.objects.all(), required=True
    )
    calificaciones = CalificacionSerializer(many=True, required=True)

    class Meta:
        model = models.Calificacion
        fields = ["fecha", "calificaciones", "evaluacion"]
        extra_kwargs = {"fecha": {"input_formats": settings.DATE_INPUT_FORMAT}}

    def create(self, validated_data):
        c = [item for item in validated_data["calificaciones"]]
        for item in c:
            item["evaluacion"] = validated_data["evaluacion"]
            item["fecha"] = validated_data["fecha"]

        calificaciones = [models.Calificacion(**item) for item in c]
        return models.Calificacion.objects.bulk_create(calificaciones)

    def validate(self, data):
        """
        Verificar que pertenzcan a ese curso los alumnos
        Tambien que no esten repetidos
        Verificar todo con institucion
        """

        alumnos = [a["alumno"].pk for a in data["calificaciones"]]
        if len(set(alumnos)) != len(alumnos):
            raise serializers.ValidationError("Existen alumnos repetidos")
        institucion = self.context["request"].user.institucion_id
        alumnos_institucion = [
            a["alumno"].institucion_id for a in data["calificaciones"]
        ]
        if not all(map(lambda a: a == institucion, alumnos_institucion)):
            raise serializers.ValidationError("Algunos alumnos no existen")

        if not all(map(lambda a: a == institucion, alumnos_institucion)):
            raise serializers.ValidationError("Algunos alumnos no existen")
        anio_lectivo = data["evaluacion"].anio_lectivo
        alumnos = Alumno.objects.filter(id__in=alumnos)
        cursos = []
        for alumno in alumnos:
            res = AlumnoCurso.objects.get(
                anio_lectivo_id=anio_lectivo.pk, alumno_id=alumno.pk
            )
            # Tiene que tener que cursar en algun lado para ese año lectivo
            if not res:
                raise serializers.ValidationError(
                    "El alumno no tiene un curso en ese año lectivo"
                )
            count = Calificacion.objects.filter(
                alumno_id=alumno.pk, evaluacion_id=data["evaluacion"].pk
            ).count()
            if count != 0:
                raise serializers.ValidationError(
                    "Ya existen calificaciones para el alumno {}".format(
                        alumno.pk
                    )
                )
            # Checkeo que el año de la evaluacion sea el año del curso
            if res.curso.anio.pk != data["evaluacion"].materia.anio.pk:
                raise serializers.ValidationError(
                    "La evaluacion es de una \
                        materia que el alumno no ha cursado!"
                )
            cursos.append(res.curso_id)
        # Chequeo que todos los cursos sean iguales, sino
        # Puede pasar que este asignando a los de A y del B a la vez
        if len(set(cursos)) != 1:
            raise serializers.ValidationError(
                "Los alumnos no pertencen al mismo curso!"
            )
        return data


class EditCalificacionSerializer(serializers.ModelSerializer):
    puntaje = serializers.FloatField(required=False, min_value=0, max_value=10)
    fecha = serializers.DateField(required=False)

    class Meta:
        model = models.Calificacion
        fields = ["puntaje", "fecha"]
        extra_kwargs = {"fecha": {"input_formats": settings.DATE_INPUT_FORMAT}}


class DeleteManyCalificacionSerializer(serializers.Serializer):
    evaluacion = serializers.PrimaryKeyRelatedField(
        queryset=Evaluacion.objects.all(), required=True
    )
    curso = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(), required=True
    )

    def validate(self, data):
        """
        Verificar todo con institucion
        """
        institucion = self.context["request"].user.institucion_id
        get_object_or_404(
            Evaluacion.objects.filter(
                anio_lectivo__institucion_id=institucion
            ),
            pk=data["evaluacion"].pk,
        )
        get_object_or_404(
            Curso.objects.filter(anio__carrera__institucion_id=institucion),
            pk=data["curso"].pk,
        )
        return data


class SinglePromedioSerializer(serializers.Serializer):
    nombre_materia = serializers.CharField(required=True)
    promedio = serializers.FloatField(required=True, min_value=0, max_value=10)


class PromedioCalificacionSerializer(serializers.Serializer):

    promedios = SinglePromedioSerializer(many=True, required=True)
    promedio_general = serializers.FloatField(
        required=False, min_value=0, max_value=10
    )
    alumno = serializers.IntegerField(required=True)


class SingleNotaFinalCalificacionSerializer(serializers.Serializer):
    nombre_materia = serializers.CharField(required=True)
    nota_final = serializers.FloatField(
        required=True, min_value=0, max_value=10
    )


class NotaFinalCalificacionSerializer(serializers.Serializer):

    notas_finales = SingleNotaFinalCalificacionSerializer(
        many=True, required=True
    )
    promedio_general = serializers.FloatField(
        required=False, min_value=0, max_value=10
    )
    alumno = serializers.IntegerField(required=True)
