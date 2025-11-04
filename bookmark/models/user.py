from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """Custom user model"""

    email = models.EmailField(_("email_address"), unique=True)
    nickname = models.CharField(_("nickname"), max_length=150)
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "designates_whether_user_active"
        ),
    )
    email_verified_at = models.DateTimeField(_("email_verified_at"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.nickname or self.email


class UserProfile(models.Model):
    """User profile model"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    email_notification = models.BooleanField(_("email_notification"), default=True)
    browser_notification = models.BooleanField(_("browser_notification"), default=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    class Meta:
        verbose_name = _("user_profile")
        verbose_name_plural = _("user_profiles")

    def __str__(self):
        return f"{self.user.nickname or self.user.email} のプロファイル"


class EmailConfirmationToken(models.Model):
    """Email confirmation token"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_tokens",
        verbose_name=_("user"),
    )
    token = models.UUIDField(_("token"), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires_at"))

    class Meta:
        verbose_name = _("email_confirmation_token")
        verbose_name_plural = _("email_confirmation_tokens")

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_valid(self):
        """トークンが有効かどうかを確認する"""
        return timezone.now() <= self.expires_at


class PasswordResetToken(models.Model):
    """Password reset token"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_tokens",
        verbose_name=_("user"),
    )
    token = models.UUIDField(_("token"), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires_at"))

    class Meta:
        verbose_name = _("password_reset_token")
        verbose_name_plural = _("password_reset_tokens")

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_valid(self):
        """トークンが有効かどうかを確認する"""
        return timezone.now() <= self.expires_at
