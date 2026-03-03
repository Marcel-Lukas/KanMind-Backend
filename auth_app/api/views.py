from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, CustomAuthTokenSerializer


def get_token_response(user: User) -> dict:
    token, _created = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.username,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return Response(get_token_response(user), status=status.HTTP_201_CREATED)



class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        data = get_token_response(user)
        return Response(data, status=status.HTTP_200_OK)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = getattr(request.user, "auth_token", None)
        if token:
            token.delete()

        return Response(
            {"detail": "Logout successful. Token has been deleted."},
            status=status.HTTP_200_OK,
        )
    

