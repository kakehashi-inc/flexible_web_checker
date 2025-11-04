from django import forms
from bookmark.models import Collection


class CollectionForm(forms.ModelForm):
    """コレクションフォーム"""

    class Meta:
        model = Collection
        fields = ("name",)
