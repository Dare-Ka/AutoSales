from rest_framework import generics

from autosales.models import User
from autosales.serializers.user import UserSerializer


class RegisterAccountView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
