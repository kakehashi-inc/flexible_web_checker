from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """カスタムユーザーモデル"""

    email = models.EmailField(_("メールアドレス"), unique=True)
    nickname = models.CharField(_("ニックネーム"), max_length=150)
    is_active = models.BooleanField(
        _("有効"),
        default=False,
        help_text=_(
            "このユーザーがアクティブかどうかを指定します。アカウントを削除する代わりに、これを選択解除してください。"
        ),
    )
    email_verified_at = models.DateTimeField(_("メール認証日時"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname"]

    class Meta:
        verbose_name = _("ユーザー")
        verbose_name_plural = _("ユーザー")

    def __str__(self):
        return self.nickname or self.email




class UserProfile(models.Model):
    """ユーザープロファイルモデル"""


    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("ユーザー"),
    )
    email_notification = models.BooleanField(_("メール通知"), default=True)
    browser_notification = models.BooleanField(_("ブラウザ通知"), default=True)
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新日時"), auto_now=True)

    class Meta:
        verbose_name = _("ユーザープロファイル")
        verbose_name_plural = _("ユーザープロファイル")

    def __str__(self):
        return f"{self.user.nickname or self.user.email} のプロファイル"


class EmailConfirmationToken(models.Model):
    """メールアドレス確認用トークン"""


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_tokens",
        verbose_name=_("ユーザー"),
    )
    token = models.UUIDField(_("トークン"), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)
    expires_at = models.DateTimeField(_("有効期限"))

    class Meta:
        verbose_name = _("メール確認トークン")
        verbose_name_plural = _("メール確認トークン")

    def __str__(self):
        return f"{self.user.email} - {self.token}"


    def is_valid(self):
        """トークンが有効かどうかを確認する"""
        return timezone.now() <= self.expires_at


class PasswordResetToken(models.Model):
    """パスワードリセット用トークン"""


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_tokens",
        verbose_name=_("ユーザー"),
    )
    token = models.UUIDField(_("トークン"), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)
    expires_at = models.DateTimeField(_("有効期限"))

    class Meta:
        verbose_name = _("パスワードリセットトークン")
        verbose_name_plural = _("パスワードリセットトークン")

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_valid(self):
        """トークンが有効かどうかを確認する"""
        return timezone.now() <= self.expires_at
