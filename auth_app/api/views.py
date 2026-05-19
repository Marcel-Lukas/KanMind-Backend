"""Auth API views for registration, login, and logout."""

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomAuthTokenSerializer, RegistrationSerializer


def build_token_response(user):
    """Build the standardised auth response payload for a given user."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'fullname': user.username,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(generics.CreateAPIView):
    """Register a new user and immediately return auth token data."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        """Validate payload, persist user, and return token response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_token_response(user), status=status.HTTP_201_CREATED)


class CustomLoginView(APIView):
    """Authenticate user credentials and return token payload."""

    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request):
        """Run serializer-based authentication flow."""
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(build_token_response(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Invalidate the current user's token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete the existing token if present."""
        token = getattr(request.user, 'auth_token', None)
        if token is not None:
            token.delete()
        return Response(
            {'detail': 'Logout successful. Token has been deleted.'},
            status=status.HTTP_200_OK,
        )
