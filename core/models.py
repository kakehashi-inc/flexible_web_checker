from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from url_manager.models import UrlItem


class Notification(models.Model):
    """通知モデル"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("ユーザー"),
    )
    url_item = models.ForeignKey(
        UrlItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("URL項目"),
    )
    message = models.TextField(_("メッセージ"))
    is_read = models.BooleanField(_("既読"), default=False)
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)

    class Meta:
        verbose_name = _("通知")
        verbose_name_plural = _("通知")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.nickname or self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
