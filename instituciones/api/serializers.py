from rest_framework import serializers
from instituciones.models import Institucion


class CreateInstitucionSerializer(serializers.Serializer):

    nombre = serializers.CharField(max_length=200, required=True)
    direccion = serializers.CharField(max_length=250, required=False)
    pais = serializers.CharField(max_length=250, required=False)
    identificador = serializers.CharField(max_length=250, required=False)
    descripcion = serializers.CharField(required=False)
    logo = serializers.ImageField(required=False)

    def create(self, validated_data):
        """
        Crear y retornar una instancia de Institucion
        """
        return Institucion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Editar y retornar una instancia de Institucion
        """
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.direccion = validated_data.get(
            'direccion', instance.direccion)
        instance.pais = validated_data.get('pais', instance.pais)
        instance.identificador = validated_data.get(
            'identificador', instance.identificador)
        instance.descripcion = validated_data.get(
            'descripcion', instance.descripcion)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.save()
        return instance


class InstitucionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institucion
        fields = '__all__'
        read_only_fields = ['activa', 'fecha_creacion', 'id']


class InstitucionStatusSerializer(serializers.ModelSerializer):

    activa = serializers.BooleanField(required=True)

    class Meta:
        model = Institucion
        fields = ['activa']


class BadRequestSerializer(serializers.Serializer):
    nombre_campo = serializers.CharField()
    detail = serializers.StringRelatedField(many=True)


class UnauthorizedSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ForbiddenSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ServerErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class NotFoundSerializer(serializers.Serializer):
    detail = serializers.CharField()
