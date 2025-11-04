from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UrlItem(models.Model):
    """URL model"""

    CHECK_TYPE_CHOICES = [
        ("RSS", _("check_type_rss")),
        ("HTML_STANDARD", _("check_type_html_standard")),
        ("HTML_CUSTOM", _("check_type_html_custom")),
    ]

    HTML_CUSTOM_CONDITION_CHOICES = [
        ("OR", _("html_condition_or")),
        ("AND", _("html_condition_and")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="url_items",
        verbose_name=_("user"),
    )
    url = models.URLField(_("url"), max_length=2000)
    title = models.CharField(_("title"), max_length=255)
    thumbnail = models.ImageField(
        _("thumbnail"), upload_to="thumbnails/", null=True, blank=True
    )
    check_type = models.CharField(
        _("check_type"), max_length=20, choices=CHECK_TYPE_CHOICES
    )
    html_selector = models.TextField(
        _("html_selector"),
        null=True,
        blank=True,
        help_text=_("separate_selectors_with_newlines"),
    )
    html_custom_condition = models.CharField(
        _("html_custom_condition"),
        max_length=5,
        choices=HTML_CUSTOM_CONDITION_CHOICES,
        default="OR",
        null=True,
        blank=True,
    )
    last_checked_at = models.DateTimeField(_("last_checked_at"), null=True, blank=True)
    last_updated_at = models.DateTimeField(_("last_updated_at"), null=True, blank=True)
    last_content_hash = models.TextField(
        _("last_content_hash"), null=True, blank=True
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)
    error_count = models.IntegerField(_("error_count"), default=0)
    last_error_message = models.TextField(
        _("last_error_message"), null=True, blank=True
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("url_item")
        verbose_name_plural = _("url_items")
        ordering = ["-last_updated_at", "-created_at"]

    def __str__(self):
        return str(self.title) if self.title else str(self.url)
