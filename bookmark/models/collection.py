from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Collection(models.Model):
    """Collection model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name=_("user"),
    )
    name = models.CharField(_("name"), max_length=255)
    order = models.IntegerField(_("order"), default=0)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    class Meta:
        verbose_name = _("collection")
        verbose_name_plural = _("collections")
        ordering = ["order", "name"]

    def __str__(self):
        return str(self.name)


class UrlItemCollection(models.Model):
    """URL item and collection intermediate model"""

    url_item = models.ForeignKey(
        "UrlItem",
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name=_("url_item"),
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="url_items",
        verbose_name=_("collection"),
    )
    added_at = models.DateTimeField(_("added_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("url_item_collection")
        verbose_name_plural = _("url_item_collections")
        unique_together = [["url_item", "collection"]]
