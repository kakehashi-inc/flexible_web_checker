from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from bookmark.models import User, EmailConfirmationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "nickname",
        "is_active",
        "email_verified_at",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("email", "nickname", "username")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("email", "username", "nickname", "password")}),
        (
            _("権限"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("重要な日付"),
            {"fields": ("last_login", "date_joined", "email_verified_at")},
        ),
    )


@admin.register(EmailConfirmationToken)
class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at")
    search_fields = ("user__email", "token")
    ordering = ("-created_at",)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at")
    search_fields = ("user__email", "token")
    ordering = ("-created_at",)
