from rest_framework.serializers import ModelSerializer
from autosales.models import User, Contact


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ("id",)
        extra_kwargs = {"user": {"write_only": True}}


class UserSerializer(ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "contacts",
        )
        read_only_fields = ("id",)
