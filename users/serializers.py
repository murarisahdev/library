from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError



class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class AuthCustomTokenSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        if email_or_username and password:

            if email_or_username:
                try:
                    user_request = get_object_or_404(
                            User,
                            username=email_or_username,
                        )
                except Exception:
                    user_request = get_object_or_404(
                        User,
                        email=email_or_username,
                    )

            user = authenticate(
                username=user_request.username,
                password=password)

            if user:
                if not user.is_active:
                    raise ValidationError(
                        'User account is disabled.')

            else:
                raise ValidationError(
                    'Unable to log in with provided credentials.')

        else:
            raise ValidationError(
                'Must include "email or username" and "password"')

        attrs['user'] = user
        return attrs