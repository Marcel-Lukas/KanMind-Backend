"""Serializers for registration and token-based login."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new ``User`` from registration payload."""

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']

    def validate_email(self, value):
        """Ensure each email is unique across users."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Check password confirmation and Django password rules."""
        password = attrs.get('password')
        repeated_password = attrs.get('repeated_password')

        if password != repeated_password:
            raise serializers.ValidationError({
                'repeated_password': 'Passwords do not match.'
            })

        validate_password(password)

        return attrs

    def create(self, validated_data):
        """Create a user and split ``fullname`` into first/last name."""
        fullname = validated_data.pop('fullname', '').strip()
        validated_data.pop('repeated_password')

        first_name, last_name = ('', '')
        if fullname:
            parts = fullname.split(' ', 1)
            first_name = parts[0]
            if len(parts) > 1:
                last_name = parts[1]

        email = validated_data['email']

        user = User(
            username=f"{first_name} {last_name}".strip(),
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    """Authenticate a user by email and password."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        """Resolve email to username and authenticate credentials."""
        email = (attrs.get('email') or '').strip().lower()
        password = attrs.get('password') or ''

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid login details!'})

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError({'detail': 'Invalid login details!'})

        attrs['user'] = user
        return attrs
    
