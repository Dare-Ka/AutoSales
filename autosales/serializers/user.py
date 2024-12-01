from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from autosales.models import User, Contact


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

        def validate(self, data):
            if data["city"] or data["street"] or data["phone"] is None:
                raise ValidationError(
                    "Поля 'Город', 'Улица' и 'Номер телефона' обязательны"
                )
            return data

        def validate_phone(self, data):
            if len(data["phone"][1:]) != 11:
                raise ValidationError(
                    "Номер телефона должен содержать 11 символов, не считая знака '+'"
                )


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

        def validate(self, data):
            if (
                data["username"]
                or data["first_name"]
                or data["last_name"]
                or data["email"] is None
            ):
                raise ValidationError("Поля 'username', 'Имя' и 'Фамилия' обязательны")
            return data
