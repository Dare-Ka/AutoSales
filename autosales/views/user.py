from os import error

from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
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
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if "password" in request.data:
            try:
                validate_password(request.data["password"])
            except ValidationError as error:
                return JsonResponse(
                    {"Status": False, "Errors": {"password": str(error)}}
                )
            else:
                request.user.set_password(request.data["password"])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

