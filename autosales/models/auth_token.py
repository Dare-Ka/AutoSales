from typing import Optional

from django.utils.translation import gettext_lazy as _
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

from .user import User



class ConfirmEmailToken(models.Model):
    @staticmethod
    def generate_key() -> str:
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name="confirm_email_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("When was this token generated")
    )

    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    def save(self, *args: Optional[tuple], **kwargs: Optional[dict]) -> None:
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Токен подтверждения Email"
        verbose_name_plural = "Токены подтверждения Email"

    def __str__(self) -> str:
        return f"Password reset token for user {self.user}"