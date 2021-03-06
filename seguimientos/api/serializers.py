from rest_framework import serializers
from seguimientos import models
from curricula.models import Materia, AnioLectivo
from users.models import User
from ontrack import settings
from alumnos.models import AlumnoCurso
import datetime
from alumnos.api.serializers import PartialViewAlumnoCursoSerializer
from curricula.api.serializers.materia import PartialViewMateriasSerializer
from users.api.serializers import PartialViewUserSeralizer


class NombreSeguimientoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)

    class Meta:
        model = models.Seguimiento
        fields = ["nombre"]


class ListSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seguimiento
        fields = [
            "id",
            "nombre",
            "descripcion",
            "en_progreso",
            "fecha_inicio",
            "fecha_cierre",
        ]


class ViewIntegranteSerializer(serializers.ModelSerializer):
    rol = serializers.StringRelatedField(read_only=True)
    usuario = PartialViewUserSeralizer()

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
            if data["rol"].nombre == "Encargado":
                raise serializers.ValidationError(
                    "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
                        data["usuario"].groups.name
                    )
                )

        return data


class EditIntegranteListSerializer(serializers.ListSerializer):
    def create(self, validated_data):

        integrantes = [
            models.IntegranteSeguimiento(**item) for item in validated_data
        ]
        return models.IntegranteSeguimiento.objects.bulk_create(integrantes)

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

        for int_id, integrante in int_mapping.items():
            if int_id not in data_mapping:
                if integrante.rol.nombre == "Encargado":
                    raise serializers.ValidationError(
                        detail="No se pueden eliminar encargados!"
                    )

        # Eliminar integrantes
        for int_id, integrante in int_mapping.items():
            if int_id not in data_mapping:
                if integrante.rol.nombre != "Encargado":
                    integrante.delete()
                else:
                    raise serializers.ValidationError(
                        detail="No se pueden eliminar encargados!"
                    )

        # Crear y actualizar los integrantes existentes.
        ret = []
        for int_id, data in data_mapping.items():
            e = int_mapping.get(int_id, None)
            if e is not None:
                ret.append(self.child.update(e, data))
        for data in data_mapping[0]:
            data.seguimiento_id = seguimiento.pk
            ret.append(self.child.create(data))

        return ret

    def validate(self, data):
        seguimiento = []
        for integrante in data:
            seguimiento.append(integrante["seguimiento"])
            if integrante["usuario"].groups.name != "Pedagogía":
                if integrante["rol"].nombre == "Encargado":
                    raise serializers.ValidationError(
                        "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
                            integrante["usuario"].groups.name
                        )
                    )

        if len(set(seguimiento)) != 1:
            raise serializers.ValidationError(
                detail="No se pueden elegir distintos seguimientos!"
            )

        return data


class EditIntegranteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    seguimiento = serializers.PrimaryKeyRelatedField(
        queryset=models.Seguimiento.objects.all(), required=True
    )
    rol = serializers.PrimaryKeyRelatedField(
        queryset=models.RolSeguimiento.objects.all(), required=True
    )
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )

    class Meta:
        model = models.IntegranteSeguimiento
        fields = ["id", "seguimiento", "rol", "usuario"]
        list_serializer_class = EditIntegranteListSerializer


class ViewSeguimientoSerializer(serializers.ModelSerializer):
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all()
    )
    descripcion = serializers.CharField(required=True)
    nombre = serializers.CharField(required=True)
    alumnos = PartialViewAlumnoCursoSerializer(many=True)
    materias = PartialViewMateriasSerializer(many=True)
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
            "fecha_creacion",
            "anio_lectivo",
            "alumnos",
            "integrantes",
            "materias",
        ]


class CreateSeguimientoSerializer(serializers.ModelSerializer):
    descripcion = serializers.CharField(required=True)
    nombre = serializers.CharField(required=True)
    fecha_cierre = serializers.DateField(
        required=True, input_formats=settings.DATE_INPUT_FORMAT
    )
    alumnos = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=True, required=True
    )
    materias = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), many=True, required=True
    )
    integrantes = CreateIntegranteSerializer(required=True, many=True)
    anio_lectivo = serializers.PrimaryKeyRelatedField(
        queryset=AnioLectivo.objects.all(), required=True
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
        if "integrantes" in data:
            integrantes = data["integrantes"]
            if len(integrantes) == 0:
                raise serializers.ValidationError(
                    "Se deben agregar al menos 1 integrante!"
                )
            encargados = 0
            for integrante in integrantes:
                if integrante["usuario"].groups.name != "Pedagogía":
                    if integrante["rol"].nombre == "Encargado":
                        raise serializers.ValidationError(
                            "Una cuenta de tipo {} no puede ser encargado/a de Seguimiento!".format(
                                integrante["usuario"].groups.name
                            )
                        )
                else:
                    if integrante["rol"].nombre == "Encargado":
                        encargados += 1
            if encargados == 0:
                raise serializers.ValidationError(
                    "Se deben agregar al menos 1 encargado!"
                )
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
            cant_materias = len(materias)
            if cant_materias > 1:
                anio_ids = set([mat.anio.pk for mat in materias])
                if len(anio_ids) != 1:
                    raise serializers.ValidationError(
                        detail="No se pueden elegir materias de distintos años!"
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

    class Meta:
        model = models.Seguimiento
        fields = [
            "nombre",
            "fecha_cierre",
            "descripcion",
        ]

    def validate(self, data):
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
        if (
            seguimiento.fecha_cierre < datetime.date.today()
            or seguimiento.fecha_cierre < seguimiento.anio_lectivo.fecha_desde
            or seguimiento.fecha_cierre > seguimiento.anio_lectivo.fecha_hasta
        ):
            raise serializers.ValidationError(
                detail="Fecha de cierre inválida"
            )

        seguimiento.save()
        return seguimiento


class StatusSeguimientoSerializer(serializers.ModelSerializer):
    en_progreso = serializers.BooleanField(required=True)

    class Meta:
        model = models.Seguimiento
        fields = ["en_progreso"]

    def update(self, seguimiento):
        seguimiento.en_progreso = self.validated_data.get(
            "en_progreso", seguimiento.en_progreso
        )
        seguimiento.save()
        return seguimiento


class CreateRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = ["nombre"]


class ViewRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RolSeguimiento
        fields = "__all__"


# Solciitudes de Seguimiento


class ViewEstadoSolicitudSeguimiento(serializers.ModelSerializer):
    estado_solicitud = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.FechaEstadoSolicitudSeguimiento
        fields = ["estado_solicitud", "fecha"]


class ViewSolicitudSeguimientoSerializer(serializers.ModelSerializer):
    alumnos = PartialViewAlumnoCursoSerializer(many=True)
    estado = ViewEstadoSolicitudSeguimiento(many=True)
    creador = PartialViewUserSeralizer()

    class Meta:
        model = models.SolicitudSeguimiento
        fields = [
            "id",
            "fecha_creacion",
            "creador",
            "alumnos",
            "motivo_solicitud",
            "estado",
        ]


class CreateSolicitudSeguimientoSerializer(serializers.ModelSerializer):
    alumnos = serializers.PrimaryKeyRelatedField(
        queryset=AlumnoCurso.objects.all(), many=True, required=True
    )
    motivo_solicitud = serializers.CharField(required=True)

    class Meta:
        model = models.SolicitudSeguimiento
        fields = [
            "alumnos",
            "motivo_solicitud",
        ]

    def validate(self, data):
        if "alumnos" in data:
            anio_lectivo = [
                alumno.anio_lectivo_id for alumno in data["alumnos"]
            ]
            curso = [alumno.curso_id for alumno in data["alumnos"]]

            if len(set(anio_lectivo)) != 1 or len(set(curso)) != 1:
                raise serializers.ValidationError(detail="Alumnos invalidos")
        return data

    def create(self, validated_data):
        creador = self.context["request"].user

        sol = models.SolicitudSeguimiento(
            creador=creador,
            motivo_solicitud=validated_data.pop("motivo_solicitud"),
        )
        sol.save()
        sol.alumnos.add(*validated_data.pop("alumnos"))
        estado = models.EstadoSolicitudSeguimiento.objects.filter(
            nombre="Pendiente"
        ).first()
        f_estado = models.FechaEstadoSolicitudSeguimiento(
            solicitud=sol, estado_solicitud=estado
        )
        f_estado.save()
        return sol, f_estado


class EditSolicitudSeguimientosSerializer(serializers.ModelSerializer):
    motivo_solicitud = serializers.CharField(required=True)

    class Meta:
        model = models.SolicitudSeguimiento
        fields = ["motivo_solicitud"]

    def update(self, solicitud):
        solicitud.motivo_solicitud = self.validated_data.get(
            "motivo_solicitud", solicitud.motivo_solicitud
        )
        solicitud.save()
        return solicitud


class EstadoSolicitudSeguimiento(serializers.Serializer):
    estado = serializers.CharField(required=True)

    class Meta:
        fields = ["estado"]

    def validate(self, data):
        estados = ["Pendiente", "Aceptada", "Rechazada"]
        if data["estado"] not in estados:
            raise serializers.ValidationError(detail="Estado inválido")
        return data

    def update(self, solicitud, estado):
        estados = models.FechaEstadoSolicitudSeguimiento.objects.filter(
            solicitud=solicitud
        )
        for e in estados:
            if e.estado_solicitud.nombre != "Pendiente":
                raise serializers.ValidationError(
                    detail="No se puede cambiar el estado"
                )
        f_estado = models.FechaEstadoSolicitudSeguimiento(
            solicitud=solicitud, estado_solicitud=estado
        )
        f_estado.save()
        return solicitud
