from django import forms
from django.utils.translation import gettext_lazy as _
from bookmark.models import UrlItem


class UrlItemForm(forms.ModelForm):
    """URL項目フォーム"""

    class Meta:
        model = UrlItem
        fields = (
            "url",
            "title",
            "check_type",
            "html_selector",
            "html_custom_condition",
        )
        widgets = {
            "html_selector": forms.Textarea(
                attrs={"rows": 4, "placeholder": _("html_selector_placeholder")}
            ),
        }

    def clean_html_selector(self):
        check_type = self.cleaned_data.get("check_type")
        html_selector = self.cleaned_data.get("html_selector")

        if check_type == "HTML_CUSTOM" and not html_selector:
            raise forms.ValidationError(
                _("html_custom_selector_required")
            )

        return html_selector

    def clean_html_custom_condition(self):
        check_type = self.cleaned_data.get("check_type")
        html_custom_condition = self.cleaned_data.get("html_custom_condition")

        if check_type == "HTML_CUSTOM" and not html_custom_condition:
            return "OR"

        return html_custom_condition


class BulkUrlAddForm(forms.Form):
    """一括URL追加フォーム"""

    urls = forms.CharField(
        label=_("url_list"),
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "placeholder": _("url_bulk_placeholder")
            }
        ),
        help_text=_("url_bulk_help_text")
    )

    check_type = forms.ChoiceField(
        label=_("check_type"),
        choices=UrlItem.CHECK_TYPE_CHOICES,
        initial="HTML_STANDARD",
    )

    def clean_urls(self):
        urls = self.cleaned_data.get("urls", "")
        url_list = [url.strip() for url in urls.split("\n") if url.strip()]

        if not url_list:
            raise forms.ValidationError(_("at_least_one_url_required"))

        for url in url_list:
            if not url.startswith(("http://", "https://")):
                raise forms.ValidationError(_("invalid_url_in_list"), params={"url": url})

        return url_list
