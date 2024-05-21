from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # Get the user object based on email
        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError('A user with this email and password is not found')

        if not user.check_password(password):
            raise serializers.ValidationError('A user with this email and password is not found')

        if not user.is_verified:
            raise serializers.ValidationError('This user has not been verified')

        # Add the user object to validated data
        attrs['user'] = self.context["request"].user

        return attrs

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

        extra_kwargs = {
            'password': {'write_only': True}
        }


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=3)

    class Meta:
        fields = ['email']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token    