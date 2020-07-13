from rest_framework import serializers
from users.models import User
from django.contrib.auth.models import Group
from instituciones.api.serializers import InstitucionSerializer


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

    def save(self, institucion):
        user = User(
            email=self.validated_data["email"],
            groups=self.validated_data["groups"],
            institucion=institucion,
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


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "phone", "date_of_birth", "picture"]

    def update(self, user):
        """
        Editar y retornar una instancia de User
        """
        user.email = self.validated_data.get("email", user.email)
        user.name = self.validated_data.get("name", user.name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get(
            "date_of_birth", user.date_of_birth
        )
        user.picture = self.validated_data.get("picture", user.picture)
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        style={"input_type": "password",}, write_only=True, required=True
    )

    new_password2 = serializers.CharField(
        style={"input_type": "password",}, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ["password", "new_password", "new_password2"]
        extra_kwargs = {
            "new_password": {"write_only": True},
            "new_password2": {"write_only": True},
        }

    def save(self, user):
        old_password = self.validated_data["password"]
        new_password = self.validated_data["new_password"]
        new_password2 = self.validated_data["new_password2"]

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"password": "Incorrect current password!"}
            )

        if new_password != new_password2:
            raise serializers.ValidationError(
                {"password": "Passwords do not match!"}
            )

        if old_password == new_password:
            raise serializers.ValidationError(
                {
                    "password": "Your new password should be different than the current one"
                }
            )

        user.set_password(new_password)
        user.save()
        return user


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class ListUserSerializer(serializers.ModelSerializer):
    institucion = InstitucionSerializer(many=False)
    groups = GroupSerializer(many=False)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "phone",
            "date_of_birth",
            "picture",
            "groups",
            "institucion",
        ]
