from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from bookmark.models import User


class UserRegistrationForm(forms.ModelForm):
    """ユーザー登録フォーム"""

    password1 = forms.CharField(
        label=_("password"),
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label=_("password_confirm"), widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "username", "nickname", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("passwords_do_not_match"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """ユーザーログインフォーム"""

    email = forms.EmailField(label=_("email_address"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    """マイページ編集フォーム"""

    class Meta:
        model = User
        fields = ("nickname", "username")


class PasswordResetRequestForm(forms.Form):
    """パスワードリセットリクエストフォーム"""

    email = forms.EmailField(label=_("email_address"))


class PasswordResetForm(forms.Form):
    """パスワードリセットフォーム"""

    password = forms.CharField(
        label=_("new_password"),
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    password_confirm = forms.CharField(
        label=_("new_password_confirm"), widget=forms.PasswordInput
    )

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_("passwords_do_not_match"))
        return password_confirm
