from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from django.contrib.auth.models import Group, Permission


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={
            'input_type': 'password',
        },
        write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'groups']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            email=self.validated_data['email'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match!'})

        user.set_password(password)
        user.save()
        return user


class GroupSerializer(serializers.ModelSerializer):

    permissions = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
