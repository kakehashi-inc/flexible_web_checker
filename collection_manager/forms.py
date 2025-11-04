from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Collection


class CollectionForm(forms.ModelForm):
    """コレクションフォーム"""

    class Meta:
        model = Collection
        fields = ("name",)
