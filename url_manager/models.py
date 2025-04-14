from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UrlItem(models.Model):
    """URLモデル"""

    CHECK_TYPE_CHOICES = [
        ("RSS", "RSSフィード"),
        ("HTML_STANDARD", "HTML標準"),
        ("HTML_CUSTOM", "HTMLカスタム"),
    ]

    HTML_CUSTOM_CONDITION_CHOICES = [
        ("OR", "いずれか変更 (OR)"),
        ("AND", "すべて変更 (AND)"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="url_items",
        verbose_name=_("ユーザー"),
    )
    url = models.URLField(_("URL"), max_length=2000)
    title = models.CharField(_("タイトル"), max_length=255)
    thumbnail = models.ImageField(
        _("サムネイル"), upload_to="thumbnails/", null=True, blank=True
    )
    check_type = models.CharField(
        _("チェックタイプ"), max_length=20, choices=CHECK_TYPE_CHOICES
    )
    html_selector = models.TextField(
        _("HTMLセレクタ"),
        null=True,
        blank=True,
        help_text=_("複数のセレクタを指定する場合は、改行で区切ってください"),
    )
    html_custom_condition = models.CharField(
        _("HTMLカスタム条件"),
        max_length=5,
        choices=HTML_CUSTOM_CONDITION_CHOICES,
        default="OR",
        null=True,
        blank=True,
    )
    last_checked_at = models.DateTimeField(_("最終チェック日時"), null=True, blank=True)
    last_updated_at = models.DateTimeField(_("最終更新日時"), null=True, blank=True)
    last_content_hash = models.TextField(
        _("最終コンテンツハッシュ"), null=True, blank=True
    )
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新日時"), auto_now=True)
    error_count = models.IntegerField(_("エラー回数"), default=0)
    last_error_message = models.TextField(
        _("最終エラーメッセージ"), null=True, blank=True
    )
    is_active = models.BooleanField(_("有効"), default=True)

    class Meta:
        verbose_name = _("URL項目")
        verbose_name_plural = _("URL項目")
        ordering = ["-last_updated_at", "-created_at"]

    def __str__(self):
        return str(self.title) if self.title else str(self.url)
