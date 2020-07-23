from rest_framework import serializers
from curricula import models
from instituciones.api.serializers import InstitucionSerializer
from ontrack import settings
import datetime


class AnioLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnioLectivo
        fields = ["nombre", "fecha_desde", "fecha_hasta"]
        extra_kwargs = {
            "nombre": {"required": True},
            "fecha_desde": {
                "required": True,
                "input_formats": settings.DATE_INPUT_FORMAT,
            },
            "fecha_hasta": {
                "required": True,
                "input_formats": settings.DATE_INPUT_FORMAT,
            },
        }
        read_only_fields = ["id", "fecha_creacion"]

    def validate(self, data):
        if data["fecha_desde"] >= data["fecha_hasta"]:
            raise serializers.ValidationError(
                "La fecha de inicio del Año Lectivo debe ser menor a la fecha fin"
            )
        return data

    def create(self, institucion):
        anio_lectivo = models.AnioLectivo(**self.validated_data)
        anio_lectivo.institucion = institucion
        anio_lectivo.save()


class EditAnioLectivoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    fecha_desde = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )
    fecha_hasta = serializers.DateField(
        required=False, input_formats=settings.DATE_INPUT_FORMAT
    )

    class Meta:
        model = models.AnioLectivo
        fields = ["nombre", "fecha_desde", "fecha_hasta"]

    def get_existing_anio_lectivo(self, anio_lectivo):
        self.anio_lectivo = anio_lectivo

    def validate(self, data):
        fecha_desde_temp = data.get(
            "fecha_desde", self.anio_lectivo.fecha_desde
        )
        fecha_hasta_temp = data.get(
            "fecha_hasta", self.anio_lectivo.fecha_hasta
        )
        if fecha_desde_temp >= fecha_hasta_temp:
            raise serializers.ValidationError(
                {
                    "detail": "La fecha de inicio del Año Lectivo debe ser menor a la fecha fin"
                }
            )
        if (
            data.get("fecha_desde", None) is not None
            or data.get("fecha_hasta", None) is not None
        ):
            if datetime.date.today() > self.anio_lectivo.fecha_desde:
                raise serializers.ValidationError(
                    "No se puede modificar el Año Lectivo luego de que ya comenzó"
                )
        return data

    def update(self, instance):
        instance.nombre = self.validated_data.get("nombre", instance.nombre)
        instance.fecha_desde = self.validated_data.get(
            "fecha_desde", instance.fecha_desde
        )
        instance.nombre = self.validated_data.get(
            "fecha_hasta", instance.fecha_hasta
        )
        instance.save()


class ViewAnioLectivoSerializer(serializers.ModelSerializer):
    institucion = InstitucionSerializer(many=False)

    class Meta:
        model = models.AnioLectivo
        fields = ["id", "nombre", "fecha_desde", "fecha_hasta", "institucion"]
