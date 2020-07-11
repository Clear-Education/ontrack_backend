from rest_framework import serializers
from instituciones.models import Institucion


class InstitucionSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=200, required=True)
    direccion = serializers.CharField(max_length=250, required=False)
    pais = serializers.CharField(max_length=250, required=False)
    identificador = serializers.CharField(max_length=250, required=False)
    descripcion = serializers.CharField(required=False)
    logo = serializers.ImageField(required=False)
    activa = serializers.BooleanField(default=True, read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)

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


# class InstitucionEstadoSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(read_only=True)
#     activa = serializers.BooleanField(required=True)

#     class Meta:
#         model = Institucion

#     def update(self, instance, validated_data):
#         if instance.activa != validated_data.get('activa')