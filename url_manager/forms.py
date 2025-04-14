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


class BulkUrlAddForm(forms.Form):
    """複数URL一括追加フォーム"""
    urls = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': _('https://example.com\nhttps://anotherexample.org\n...')}),
        label=_('URLリスト (改行区切り)'),
        help_text=_('追加したいURLを改行で区切って入力してください。')
    )

    def clean_urls(self):
        urls_text = self.cleaned_data.get('urls', '')
        url_list = [url.strip() for url in urls_text.splitlines() if url.strip()]
        if not url_list:
            raise forms.ValidationError(_('少なくとも1つのURLを入力してください。'))
        return url_list
