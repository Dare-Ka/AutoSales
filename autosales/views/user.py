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
