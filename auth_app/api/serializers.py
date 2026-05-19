"""Serializers for registration and token-based login."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new ``User`` from registration payload."""

    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']

    def validate_email(self, value):
        """Ensure each email is unique across users."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def validate(self, attrs):
        """Check password confirmation and Django password rules."""
        if attrs.get('password') != attrs.get('repeated_password'):
            raise serializers.ValidationError({
                'repeated_password': 'Passwords do not match.',
            })

        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        """Create a user and split ``fullname`` into first/last name."""
        fullname = validated_data.pop('fullname', '').strip()
        validated_data.pop('repeated_password')

        first_name, last_name = self._split_fullname(fullname)

        user = User(
            username=f'{first_name} {last_name}'.strip(),
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    @staticmethod
    def _split_fullname(fullname):
        """Split ``fullname`` into first/last name parts."""
        if not fullname:
            return '', ''
        parts = fullname.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name


class CustomAuthTokenSerializer(serializers.Serializer):
    """Authenticate a user by email and password."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )

    default_error_messages = {
        'invalid_credentials': 'Invalid login details!',
    }

    def validate(self, attrs):
        """Resolve email to username and authenticate credentials."""
        email = (attrs.get('email') or '').strip().lower()
        password = attrs.get('password') or ''

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            self._fail_authentication()

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            self._fail_authentication()

        attrs['user'] = user
        return attrs

    def _fail_authentication(self):
        """Raise a uniform error message for invalid credentials."""
        raise serializers.ValidationError(
            {'detail': self.error_messages['invalid_credentials']}
        )
