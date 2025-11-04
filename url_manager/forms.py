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
    """一括URL追加フォーム"""
    
    urls = forms.CharField(
        label=_("URL一覧"),
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "placeholder": _("URLを1行に1つずつ入力してください。\n例:\nhttps://example.com\nhttps://example.org")
            }
        ),
        help_text=_("URLを1行に1つずつ入力してください。タイトルは自動的に取得されます。")
    )
    
    check_type = forms.ChoiceField(
        label=_("チェックタイプ"),
        choices=UrlItem.CHECK_TYPE_CHOICES,
        initial="HTML_STANDARD",
    )
    
    def clean_urls(self):
        urls = self.cleaned_data.get("urls", "")
        url_list = [url.strip() for url in urls.split("\n") if url.strip()]
        
        if not url_list:
            raise forms.ValidationError(_("少なくとも1つのURLを入力してください。"))
        
        for url in url_list:
            if not url.startswith(("http://", "https://")):
                raise forms.ValidationError(_("無効なURLが含まれています: %(url)s"), params={"url": url})
        
        return url_list
