from django import forms
from django.utils.translation import gettext_lazy as _
from .models import UrlItem


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
                attrs={"rows": 4, "placeholder": _("例: div.content\n#main-content h2")}
            ),
        }

    def clean_html_selector(self):
        check_type = self.cleaned_data.get("check_type")
        html_selector = self.cleaned_data.get("html_selector")

        if check_type == "HTML_CUSTOM" and not html_selector:
            raise forms.ValidationError(
                _(
                    "HTMLカスタムチェックタイプを選択した場合は、HTMLセレクタを入力してください。"
                )
            )

        return html_selector

    def clean_html_custom_condition(self):
        check_type = self.cleaned_data.get("check_type")
        html_custom_condition = self.cleaned_data.get("html_custom_condition")

        if check_type == "HTML_CUSTOM" and not html_custom_condition:
            return "OR"

        return html_custom_condition
