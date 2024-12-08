from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from autosales.models import User
from autosales.serializers.auth_token import ConfirmEmailTokenSerializer
from autosales.serializers.user import UserSerializer


class RegisterAccountView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ConfirmAccountView(generics.CreateAPIView):
    serializer_class = ConfirmEmailTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = serializer.confirm_email(request.data)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                {"Status": False, "errors": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AccountDetails(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if "password" in request.data:
            try:
                validate_password(request.data["password"])
            except ValidationError as error:
                return Response({"Status": False, "Errors": {"password": str(error)}})
            else:
                request.user.set_password(request.data["password"])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"Status": True})
        else:
            return Response({"Status": False, "Errors": user_serializer.errors})


class LoginAccount(generics.CreateAPIView):
    serializer_class = ConfirmEmailTokenSerializer

    def create(self, request, *args, **kwargs):
        if {"email", "password"}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data["email"],
                password=request.data["password"],
            )
            if user is not None and user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {"Status": True, "Token": token.key}, status=status.HTTP_200_OK
                )

            return Response(
                {"Status": False, "Errors": "Не удалось авторизовать"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"},
            status=status.HTTP_400_BAD_REQUEST,
        )
