from rest_framework import serializers


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


STANDARD_ERRORS = {
    400: BadRequestSerializer,
    401: UnauthorizedSerializer,
    403: ForbiddenSerializer,
    404: NotFoundSerializer,
    500: ServerErrorSerializer,
}
