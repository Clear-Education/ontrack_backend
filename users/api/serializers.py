from rest_framework import serializers
from users.models import User
from django.contrib.auth.models import Group


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "password"]


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password",}, write_only=True, required=True
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=False, required=True, queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = ["email", "password", "password2", "groups"]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self):
        user = User(
            email=self.validated_data["email"],
            groups=self.validated_data["groups"],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError(
                {"password": "Passwords do not match!"}
            )

        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "groups"]


class GroupSerializer(serializers.ModelSerializer):

    permissions = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
