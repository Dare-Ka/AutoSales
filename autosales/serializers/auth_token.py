from rest_framework.serializers import ModelSerializer, ValidationError

from autosales.models import ConfirmEmailToken, User


class ConfirmEmailTokenSerializer(ModelSerializer):
    class Meta:
        model = ConfirmEmailToken
        fields = ("email", "token")
        read_only_fields = ("user",)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с данным email не найден.")
        return email

    def validate(self, attrs):
        email = attrs.get("email")
        token = attrs.get("token")

        if not ConfirmEmailToken.objects.filter(user__email=email, key=token).exists():
            raise ValidationError("Неправильно указан токен или email.")

        return attrs

    def confirm_email(self, validated_data):
        token = ConfirmEmailToken.objects.filter(
            user__email=validated_data.get("email"), key=validated_data.get("token")
        ).first()

        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return {"Status": True}
        else:
            raise ValidationError(
                {"Status": False, "Errors": "Неправильно указан токен или email"}
            )
