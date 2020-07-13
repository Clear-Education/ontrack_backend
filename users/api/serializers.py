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
    password2 = serializers.CharField(style={"input_type": "password",}, write_only=True, required=True)
    groups = serializers.PrimaryKeyRelatedField(many=False, required=True, queryset=Group.objects.all())

    class Meta:
        model = User
        fields = ["email", "password", "password2", "groups"]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self, institucion):
        user = User(email=self.validated_data["email"], groups=self.validated_data["groups"], institucion=institucion,)
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden!"})

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
        if self.validated_data["email"] is not None:
            existing_user_email = User.objects.filter(email__exact=self.validated_data["email"])
            if len(existing_user_email) > 0:
                raise serializers.ValidationError({"email": "Ya existe un usuario con ese mail registrado!"})

        user.email = self.validated_data.get("email", user.email)
        user.name = self.validated_data.get("name", user.name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get("date_of_birth", user.date_of_birth)
        user.picture = self.validated_data.get("picture", user.picture)
        user.save()
        return user


class EditOtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "phone", "date_of_birth", "picture", "groups"]

    def update(self, user):
        """
        Editar y retornar una instancia de User
        """
        if self.validated_data["email"] is not None:
            existing_user_email = User.objects.filter(email__exact=self.validated_data["email"])
            if len(existing_user_email) > 0:
                raise serializers.ValidationError({"email": "Ya existe un usuario con ese mail registrado!"})

        user.email = self.validated_data.get("email", user.email)
        user.name = self.validated_data.get("name", user.name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get("date_of_birth", user.date_of_birth)
        user.picture = self.validated_data.get("picture", user.picture)
        user.groups = self.validated_data.get("groups", user.groups)
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password",}, write_only=True, required=True)
    new_password = serializers.CharField(style={"input_type": "password",}, write_only=True, required=True)
    new_password2 = serializers.CharField(style={"input_type": "password",}, write_only=True, required=True)

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
            raise serializers.ValidationError({"password": "La contraseña ingresada es incorrecta!"})

        if new_password != new_password2:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden!"})

        if old_password == new_password:
            raise serializers.ValidationError({"password": "La nueva contraseña debe ser diferente a la actual!"})

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
        fields = ["email", "name", "phone", "date_of_birth", "picture", "groups", "institucion"]


class UserStatusSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ["is_active"]
