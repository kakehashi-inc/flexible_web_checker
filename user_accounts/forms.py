from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationForm(forms.ModelForm):
    """ユーザー登録フォーム"""
    password = forms.CharField(
        label=_('パスワード'),
        widget=forms.PasswordInput,
        validators=[validate_password]
    )
    password_confirm = forms.CharField(
        label=_('パスワード（確認）'),
        widget=forms.PasswordInput
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'nickname', 'password', 'password_confirm')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('このメールアドレスは既に使用されています。'))
        return email
        
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_('パスワードが一致しません。'))
        return password_confirm
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    """ユーザーログインフォーム"""
    email = forms.EmailField(label=_('メールアドレス'))
    password = forms.CharField(label=_('パスワード'), widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    class Meta:
        model = User
        fields = ('nickname', 'username')
        
class PasswordResetRequestForm(forms.Form):
    """パスワードリセットリクエストフォーム"""
    email = forms.EmailField(label=_('メールアドレス'))
    
class PasswordResetForm(forms.Form):
    """パスワードリセットフォーム"""
    password = forms.CharField(
        label=_('新しいパスワード'),
        widget=forms.PasswordInput,
        validators=[validate_password]
    )
    password_confirm = forms.CharField(
        label=_('新しいパスワード（確認）'),
        widget=forms.PasswordInput
    )
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_('パスワードが一致しません。'))
        return password_confirm
