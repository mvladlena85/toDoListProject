from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from toDoListProject.core.fields import PasswordField
from toDoListProject.core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)
    # password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    # password_repeat = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "password", "password_repeat")

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError({'password_repeat': 'Passwords must match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data['password'] = make_password(validated_data['password'])
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "password"]

    def create(self, validated_data: dict) -> User:
        user = authenticate(
            username=validated_data['username'],
            password=validated_data['password']
        )
        if not user:
            raise AuthenticationFailed
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UpdatePasswordSerializer(serializers.Serializer):
    model = User

    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    def validate_old_password(self, old_password: str) -> str:
        if not self.instance.check_password(old_password):
            raise ValidationError('Password is incorrect')
        return old_password

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    def create(self, validated_data):
        pass
