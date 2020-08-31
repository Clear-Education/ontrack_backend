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


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    groups = serializers.PrimaryKeyRelatedField(
        many=False, required=True, queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "groups",
            "name",
            "phone",
            "date_of_birth",
            "dni",
            "picture",
            "last_name",
            "cargo",
            "legajo",
            "direccion",
            "localidad",
            "provincia",
        ]
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
                {"password": "Las contraseñas no coinciden!"}
            )

        user.name = self.validated_data.get("name", None)
        user.phone = self.validated_data.get("phone", None)
        user.date_of_birth = self.validated_data.get("date_of_birth", None)
        user.dni = self.validated_data.get("dni", None)
        user.last_name = self.validated_data.get("last_name", None)
        user.cargo = self.validated_data.get("cargo", None)
        user.legajo = self.validated_data.get("legajo", None)
        user.picture = self.validated_data.get("picture", None)
        user.direccion = self.validated_data.get("direccion", None)
        user.localidad = self.validated_data.get("localidad", None)
        user.provincia = self.validated_data.get("provincia", None)

        user.set_password(password)
        user.save()
        return user


class EditUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    dni = serializers.IntegerField(required=False)
    legajo = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "phone",
            "date_of_birth",
            "picture",
            "dni",
            "last_name",
            "cargo",
            "legajo",
            "direccion",
            "localidad",
            "provincia",
        ]

    def update(self, user):
        """
        Editar y retornar una instancia de User
        """
        if self.validated_data["email"] is not None:
            existing_user_email = User.objects.filter(
                email__exact=self.validated_data["email"]
            ).exclude(id__exact=user.id)
            if len(existing_user_email) > 0:
                raise serializers.ValidationError(
                    {"email": "Ya existe un usuario con ese mail registrado!"}
                )

        user.name = self.validated_data.get("name", user.name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get(
            "date_of_birth", user.date_of_birth
        )
        user.dni = self.validated_data.get("dni", user.dni)
        user.last_name = self.validated_data.get("last_name", user.last_name)
        user.cargo = self.validated_data.get("cargo", user.cargo)
        user.legajo = self.validated_data.get("legajo", user.legajo)
        user.direccion = self.validated_data.get("direccion", user.direccion)
        user.localidad = self.validated_data.get("localidad", user.localidad)
        user.provincia = self.validated_data.get("provincia", user.provincia)
        user.picture = self.validated_data.get("picture", user.picture)
        user.save()
        return user


class EditOtherUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    dni = serializers.IntegerField(required=False)
    legajo = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "phone",
            "date_of_birth",
            "picture",
            "groups",
            "dni",
            "last_name",
            "cargo",
            "legajo",
            "direccion",
            "localidad",
            "provincia",
        ]

    def update(self, user):
        """
        Editar y retornar una instancia de User
        """
        if self.validated_data.get("email", None) is not None:
            existing_user_email = User.objects.filter(
                email__exact=self.validated_data["email"]
            ).exclude(id__exact=user.id)
            if len(existing_user_email) > 0:
                raise serializers.ValidationError(
                    {"email": "Ya existe un usuario con ese mail registrado!"}
                )

        user.email = self.validated_data.get("email", user.email)
        user.name = self.validated_data.get("name", user.name)
        user.phone = self.validated_data.get("phone", user.phone)
        user.date_of_birth = self.validated_data.get(
            "date_of_birth", user.date_of_birth
        )
        user.dni = self.validated_data.get("dni", user.dni)
        user.last_name = self.validated_data.get("last_name", user.last_name)
        user.cargo = self.validated_data.get("cargo", user.cargo)
        user.legajo = self.validated_data.get("legajo", user.legajo)
        user.direccion = self.validated_data.get("direccion", user.direccion)
        user.localidad = self.validated_data.get("localidad", user.localidad)
        user.provincia = self.validated_data.get("provincia", user.provincia)
        user.picture = self.validated_data.get("picture", user.picture)
        user.groups = self.validated_data.get("groups", user.groups)
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password",}, write_only=True, required=True
    )
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
                {"password": "La contraseña ingresada es incorrecta!"}
            )

        if new_password != new_password2:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden!"}
            )

        if old_password == new_password:
            raise serializers.ValidationError(
                {
                    "password": "La nueva contraseña debe ser diferente a la actual!"
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
            "id",
            "email",
            "name",
            "phone",
            "date_of_birth",
            "picture",
            "groups",
            "dni",
            "last_name",
            "cargo",
            "legajo",
            "direccion",
            "localidad",
            "provincia",
            "institucion",
            "is_active",
        ]


class UserStatusSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ["is_active"]


class LoginResponseSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=False)
    reset_token = serializers.CharField(required=False)

    groups = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "email",
            "groups",
            "name",
            "phone",
            "date_of_birth",
            "dni",
            "last_name",
            "cargo",
            "picture",
            "legajo",
            "direccion",
            "localidad",
            "provincia",
            "token",
            "reset_token",
            "institucion",
        ]
