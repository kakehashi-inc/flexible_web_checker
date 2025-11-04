from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Collection(models.Model):
    """コレクションモデル"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name=_("ユーザー"),
    )
    name = models.CharField(_("名前"), max_length=255)
    order = models.IntegerField(_("並び順"), default=0)
    created_at = models.DateTimeField(_("作成日時"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新日時"), auto_now=True)

    class Meta:
        verbose_name = _("コレクション")
        verbose_name_plural = _("コレクション")
        ordering = ["order", "name"]

    def __str__(self):
        return str(self.name)


class UrlItemCollection(models.Model):
    """URL項目とコレクションの中間テーブル"""

    url_item = models.ForeignKey(
        "UrlItem",
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name=_("URL項目"),
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="url_items",
        verbose_name=_("コレクション"),
    )
    added_at = models.DateTimeField(_("追加日時"), auto_now_add=True)

    class Meta:
        verbose_name = _("URL項目-コレクション")
        verbose_name_plural = _("URL項目-コレクション")
        unique_together = [["url_item", "collection"]]
