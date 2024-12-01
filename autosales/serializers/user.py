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
        if not attrs.get("city") or not attrs.get("street"):
            raise ValidationError(
                "Поля 'Город', 'Улица' и 'Номер телефона' обязательны"
            )
        return attrs

    def validate_phone(self, phone):
        if not phone:
            raise ValidationError(_("Поле 'Номер телефона' является обязательным"))
        if len(phone[1:]) != 11:
            raise ValidationError(
                _("Номер телефона должен содержать 11 символов, не считая знака '+'")
            )
        return phone


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
        if not attrs.get("first_name") or not attrs.get("last_name"):
            raise ValidationError(_("Поля 'username', 'Имя' и 'Фамилия' обязательны"))
        return attrs

    def validated_username(self, username):
        if not username:
            raise ValidationError(_("Поле 'username' является обязательным"))
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Пользователь с таким именем уже существует"))
        return username

    def validate_email(self, email):
        if not email:
            raise ValidationError(_("Поле 'Электронная почта' является обязательным"))
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Email уже зарегистрирован"))
        return email
