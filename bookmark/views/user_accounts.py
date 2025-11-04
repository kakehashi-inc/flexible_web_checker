from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth import views as auth_views

from bookmark.models import User, EmailConfirmationToken, PasswordResetToken
from bookmark.forms.user_accounts import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)


def register(request):
    """ユーザー登録ビュー"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is inactive until email is verified
            user.save()

            token = EmailConfirmationToken.objects.create(
                user=user,
                expires_at=timezone.now() + timezone.timedelta(seconds=settings.EMAIL_CONFIRMATION_TIMEOUT),
            )

            verification_url = request.build_absolute_uri(reverse("bookmark:verify_email", kwargs={"token": token.token}))

            subject = _("email_confirmation_subject")
            message = render_to_string(
                "email/verify_email.html",
                {
                    "user": user,
                    "verification_url": verification_url,
                    "expiration_hours": settings.EMAIL_CONFIRMATION_TIMEOUT // 3600,
                },
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message,
            )

            messages.success(request, _("registration_complete_confirm_email"))
            return redirect("bookmark:login")
    else:
        form = UserRegistrationForm()

    return render(request, "user_accounts/register.html", {"form": form})


def verify_email(request, token):
    """メールアドレス確認ビュー"""
    token_obj = get_object_or_404(EmailConfirmationToken, token=token)

    if not token_obj.is_valid():
        messages.error(request, _("token_expired_please_register_again"))
        return redirect("bookmark:register")

    user = token_obj.user
    user.is_active = True
    user.email_verified_at = timezone.now()
    user.save()

    EmailConfirmationToken.objects.filter(user=user).delete()

    messages.success(request, _("email_confirmed_please_login"))
    return redirect("bookmark:login")


def login_view(request):
    """ログインビュー"""
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get("next", "bookmark:url_list")
                    return redirect(next_url)
                else:
                    messages.error(request, _("account_not_activated"))
            else:
                messages.error(request, _("invalid_email_or_password"))
    else:
        form = UserLoginForm()

    return render(request, "user_accounts/login.html", {"form": form})


def logout_view(request):
    """ログアウトビュー"""
    logout(request)
    messages.success(request, _("logged_out"))
    return redirect("bookmark:login")


@login_required
def profile(request):
    """マイページビュー"""
    return render(request, "user_accounts/mypage.html", {"user": request.user})


@login_required
def edit_profile(request):
    """マイページ編集ビュー"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("mypage_updated"))
            return redirect("bookmark:mypage")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "user_accounts/edit_profile.html", {"form": form})


def password_reset_request(request):
    """パスワードリセットリクエストビュー"""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)

                token = PasswordResetToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + timezone.timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT),
                )

                reset_url = request.build_absolute_uri(reverse("bookmark:password_reset", kwargs={"token": token.token}))

                subject = _("password_reset_subject")
                message = render_to_string(
                    "email/password_reset.html",
                    {
                        "user": user,
                        "reset_url": reset_url,
                        "expiration_hours": settings.PASSWORD_RESET_TIMEOUT // 3600,
                    },
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=message,
                )

                messages.success(request, _("password_reset_email_sent"))
                return redirect("bookmark:login")
            except User.DoesNotExist:
                messages.success(request, _("password_reset_email_sent"))
                return redirect("bookmark:login")
    else:
        form = PasswordResetRequestForm()

    return render(request, "user_accounts/password_reset_request.html", {"form": form})


def password_reset(request, token):
    """パスワードリセットビュー"""
    token_obj = get_object_or_404(PasswordResetToken, token=token)

    if not token_obj.is_valid():
        messages.error(request, _("token_expired_reset_password_again"))
        return redirect("bookmark:password_reset_request")

    user = token_obj.user

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()

            PasswordResetToken.objects.filter(user=user).delete()

            messages.success(
                request,
                _("password_reset_success_login_message"),
            )
            return redirect("bookmark:login")
    else:
        form = PasswordResetForm()

    return render(request, "user_accounts/password_reset.html", {"form": form, "token": token})


class PasswordChangeView(auth_views.PasswordChangeView):
    """パスワード変更ビュー"""

    template_name = "registration/password_change_form.html"
    success_url = "/accounts/password/change/done/"


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """パスワード変更完了ビュー"""

    template_name = "registration/password_change_done.html"
