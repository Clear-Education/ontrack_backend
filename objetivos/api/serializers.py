from rest_framework import serializers
from objetivos.models import Objetivo, TipoObjetivo, AlumnoObjetivo
from seguimientos.models import Seguimiento
from alumnos.models import Alumno, AlumnoCurso

# from seguimientos.api.serializers import ViewSeguimientoSerializer
from alumnos.api.serializers import ViewAlumnoCursoSerializer


class CreateTipoObjetivoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True, max_length=150)
    descripcion = serializers.CharField(max_length=150, required=False)
    cuantitativo = serializers.BooleanField(required=True)
    multiple = serializers.BooleanField(required=True)
    valor_minimo = serializers.FloatField(required=False)
    valor_maximo = serializers.FloatField(required=False)

    class Meta:
        model = TipoObjetivo
        fields = [
            "nombre",
            "descripcion",
            "cuantitativo",
            "multiple",
            "valor_minimo",
            "valor_maximo",
        ]


class UpdateTipoObjetivoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False, max_length=150)
    descripcion = serializers.CharField(max_length=150, required=False)
    cuantitativo = serializers.BooleanField(required=False)
    multiple = serializers.BooleanField(required=False)
    valor_minimo = serializers.FloatField(required=False)
    valor_maximo = serializers.FloatField(required=False)

    class Meta:
        model = TipoObjetivo
        fields = [
            "nombre",
            "descripcion",
            "cuantitativo",
            "multiple",
            "valor_minimo",
            "valor_maximo",
        ]


class GetTipoObjetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoObjetivo
        fields = [
            "id",
            "nombre",
            "descripcion",
            "cuantitativo",
            "multiple",
            "valor_minimo",
            "valor_maximo",
        ]


class CreateObjetivoSerializer(serializers.ModelSerializer):
    valor_objetivo_cuantitativo = serializers.FloatField(required=False)
    descripcion = serializers.CharField(max_length=150, required=False)
    seguimiento = serializers.PrimaryKeyRelatedField(
        queryset=Seguimiento.objects.all(), many=False, required=True
    )
    tipo_objetivo = serializers.PrimaryKeyRelatedField(
        queryset=TipoObjetivo.objects.all(), many=False, required=True
    )

    class Meta:
        model = Objetivo
        fields = [
            "valor_objetivo_cuantitativo",
            "descripcion",
            "seguimiento",
            "tipo_objetivo",
        ]

    def create(self, validated_data):
        return Objetivo.objects.create(**validated_data)


class UpdateObjetivoSerializer(serializers.ModelSerializer):
    valor_objetivo_cuantitativo = serializers.FloatField(required=False)
    descripcion = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = Objetivo
        fields = [
            "valor_objetivo_cuantitativo",
            "descripcion",
        ]


class GetObjetivoSerializer(serializers.ModelSerializer):
    # Cambiar al serializer cuando exista
    # seguimiento = ViewSeguimientoSerializer(many=False)
    seguimiento = serializers.StringRelatedField()
    tipo_objetivo = GetTipoObjetivoSerializer(many=False)

    class Meta:
        model = Objetivo
        fields = [
            "id",
            "valor_objetivo_cuantitativo",
            "descripcion",
            "seguimiento",
            "tipo_objetivo",
            "fecha_creacion",
        ]


class GetAlumnoObjetivoSerializer(serializers.ModelSerializer):
    objetivo = GetObjetivoSerializer(many=False)
    alumno_curso = ViewAlumnoCursoSerializer(many=False)
    valor = serializers.FloatField(required=False)

    class Meta:
        model = AlumnoObjetivo
        fields = [
            "objetivo",
            "alumno_curso",
            "valor",
            "alcanzada",
            "fecha_creacion",
        ]


class UpdateAlumnoObjetivoSerializer(serializers.Serializer):
    alumno_curso = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=False, required=False
    )
    alumno = serializers.PrimaryKeyRelatedField(
        queryset=Alumno.objects.all(), many=False, required=False
    )
    alcanzada = serializers.BooleanField(required=True)


class ReturnId(serializers.Serializer):
    id = serializers.IntegerField()
