from rest_framework import serializers, exceptions

from tracker.authentication import JWTAuthentication
from tracker.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        return JWTAuthentication.encode_jwt_token(instance)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
            if not user.check_password(raw_password=data['password']):
                raise exceptions.AuthenticationFailed()
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        return JWTAuthentication.encode_jwt_token(user)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class RequestLogSerializer(serializers.Serializer):
    total_count = serializers.FloatField()
    total_cost = serializers.FloatField()