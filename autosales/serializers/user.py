from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from autosales.models import User, Contact
from django.utils.translation import gettext_lazy as _


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "user",
            "phone",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"user": {"write_only": True}}

    def validate(self, attrs):
        if not attrs["city"] or not attrs["street"] or not attrs["phone"]:
            raise ValidationError(
                "Поля 'Город', 'Улица' и 'Номер телефона' обязательны"
            )
        return attrs

    def validate_phone(self, attrs):
        if len(attrs["phone"][1:]) != 11:
            raise ValidationError(
                _("Номер телефона должен содержать 11 символов, не считая знака '+'")
            )
        return attrs


class UserSerializer(ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        depth = 1
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "contacts",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if (
            not attrs["username"]
            or not attrs["first_name"]
            or not attrs["last_name"]
            or not attrs["email"]
        ):
            raise ValidationError(_("Поля 'username', 'Имя' и 'Фамилия' обязательны"))
        return attrs
