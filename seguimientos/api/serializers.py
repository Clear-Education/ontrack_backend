from rest_framework import serializers
from seguimientos import models
from curricula.models import Materia, AnioLectivo
from users.models import User
from ontrack import settings
from alumnos.models import AlumnoCurso
import datetime


class ListSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "descripcion",
            "en_progreso",
            "fecha_inicio",
            "fecha_cierre",
        ]


class ViewIntegranteSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.IntegranteSeguimiento
        fields = [
            "id",
            "usuario",
            "rol",
            "fecha_desde",
            "fecha_hasta",
            "fecha_creacion",
            "seguimiento",
        ]


class CreateIntegranteSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=models.RolSeguimiento.objects.all(), required=True
    )
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )

    class Meta:
        model = models.IntegranteSeguimiento
        fields = [
            "usuario",
            "rol",
        ]

    def validate(self, data):
        if data["usuario"].groups.name != "Pedagogía":
            if data["rol"].nombre == "Encargado de Seguimiento":
                raise serializers.ValidationError(
                    "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
                        data["usuario"].groups.name
                    )
                )
        return data


class EditIntegranteListSerializer(serializers.ListSerializer):
    def update(self, instance, seguimiento):
        # Mapping id->existentes and id->nuevos.
        int_mapping = {i.id: i for i in instance}
        # data_mapping = {item["id"]: item for item in validated_data}
        data_mapping = {0: []}
        for item in self.validated_data:
            if "id" in item:
                data_mapping[item["id"]] = item
            else:
                data_mapping[0].append(item)
        # Crear y actualizar las evaluaciones existentes.
        ret = []
        for int_id, data in data_mapping.items():
            e = int_mapping.get(int_id, None)
            if e is not None:
                ret.append(self.child.update(e, data))
        for data in data_mapping[0]:
            data.seguimiento_id = seguimiento.pk
            ret.append(self.child.create(data))

        # Eliminar integrantes
        for int_id, integrante in int_mapping.items():
            if int_id not in data_mapping:
                if self.context["request"].user.pk != integrante.usuario_id:
                    integrante.delete()
        return ret

    def validate(self, data):
        for integrante in data:
            if integrante["usuario"].groups.name != "Pedagogía":
                if integrante["rol"].nombre == "Encargado de Seguimiento":
                    raise serializers.ValidationError(
                        "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
                            integrante["usuario"].groups.name
                        )
                    )
        return data


# class EditIntegranteSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(required=False)
#     rol = serializers.PrimaryKeyRelatedField(
#         queryset=models.RolSeguimiento.objects.all(), required=True
#     )
#     usuario = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(), required=True
#     )

#     class Meta:
#         model = models.IntegranteSeguimiento
#         fields = [
#             "id",
#             "usuario",
#             "rol",
#         ]
#         list_serializer_class = EditIntegranteListSerializer

#     def validate(self, data):
#         if data["usuario"].groups.name != "Pedagogía":
#             if data["rol"].nombre == "Encargado de Seguimiento":
#                 raise serializers.ValidationError(
#                     "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
#                         data["usuario"].groups.name
#                     )
#                 )
#         return data


class ViewSeguimientoSerializer(serializers.ModelSerializer):
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all()
    )
    descripcion = serializers.CharField(required=True)
    nombre = serializers.CharField(required=True)
    alumnos = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=True
    )
    materias = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), many=True, required=False
    )
    integrantes = ViewIntegranteSerializer(many=True)

    class Meta:
        model = models.Seguimiento
        fields = [
            "id",
            "nombre",
            "descripcion",
            "en_progreso",
            "fecha_inicio",
            "fecha_cierre",
            "anio_lectivo",
            "alumnos",
            "integrantes",
            "materias",
        ]


class CreateSeguimientoSerializer(serializers.ModelSerializer):
    descripcion = serializers.CharField(required=True)
    nombre = serializers.CharField(required=True)
    fecha_cierre = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )
    alumnos = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=True, required=True
    )
    materias = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), many=True, required=False
    )
    integrantes = CreateIntegranteSerializer(required=False, many=True)
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), required=False
    )

    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "fecha_cierre",
            "descripcion",
            "alumnos",
            "materias",
            "integrantes",
            "anio_lectivo",
        ]

    def validate(self, data):
        if "materias" in data:
            materias = data["materias"]
            for alumno in data["alumnos"]:
                m = Materia.objects.filter(anio_id=alumno.curso.anio_id)
                if m is None:
                    raise serializers.ValidationError(
                        detail="Materias inválidas"
                    )
                for mat in materias:
                    if mat not in m:
                        raise serializers.ValidationError(
                            detail="Materias inválidas"
                        )
        if "fecha_cierre" in data:
            if (
                data["fecha_cierre"] < datetime.date.today()
                or data["fecha_cierre"] < data["anio_lectivo"].fecha_desde
            ):
                raise serializers.ValidationError(
                    detail="Fecha de cierre inválida"
                )
        return data

    def create(self, validated_data):
        # agregar creacion de materias
        institucion_id = self.context["request"].user.institucion_id
        integrantes = []
        if "integrantes" in validated_data:
            integrantes = validated_data.pop("integrantes")
        materias = []
        if "materias" in validated_data:
            materias = validated_data.pop("materias")

        alumnos = validated_data.pop("alumnos")
        seguimiento = models.Seguimiento(
            en_progreso=True, institucion_id=institucion_id, **validated_data
        )
        seguimiento.save()

        seguimiento.alumnos.add(*alumnos)
        seguimiento.materias.add(*materias)

        for integrante in integrantes:
            i = models.IntegranteSeguimiento.objects.create(
                seguimiento=seguimiento, **integrante
            )
            i.save()
        return seguimiento


class EditSeguimientoSerializer(serializers.ModelSerializer):
    descripcion = serializers.CharField(required=False)
    nombre = serializers.CharField(required=False)
    fecha_cierre = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )
    en_progreso = serializers.BooleanField(required=False)

    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "fecha_cierre",
            "descripcion",
            "en_progreso",
        ]

    def validate(self, data):
        if "fecha_cierre" in data:
            if (
                data["fecha_cierre"] < datetime.date.today()
                or data["fecha_cierre"] < data["anio_lectivo"].fecha_desde
            ):
                raise serializers.ValidationError(
                    detail="Fecha de cierre inválida"
                )
        return data

    def update(self, seguimiento):
        seguimiento.descripcion = self.validated_data.get(
            "descripcion", seguimiento.descripcion
        )
        seguimiento.nombre = self.validated_data.get(
            "nombre", seguimiento.nombre
        )
        seguimiento.fecha_cierre = self.validated_data.get(
            "fecha_cierre", seguimiento.fecha_cierre
        )
        seguimiento.en_progreso = self.validated_data.get(
            "en_progreso", seguimiento.en_progreso
        )

        return seguimiento


class CreateRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = ["nombre"]


class ViewRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = "__all__"
