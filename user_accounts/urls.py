from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "user_accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("mypage/", views.profile, name="mypage"),
    path("mypage/edit/", views.edit_profile, name="edit_mypage"),
    path("verify-email/<uuid:token>/", views.verify_email, name="verify_email"),
    path(
        "password/reset/", views.password_reset_request, name="password_reset_request"
    ),
    path("password/reset/<uuid:token>/", views.password_reset, name="password_reset"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/accounts/password/change/done/",
        ),
        name="password_change",
    ),  # Use absolute success_url
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]
