from django.contrib import admin
from bookmark.models import UrlItem


@admin.register(UrlItem)
class UrlItemAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "user", "check_type", "is_active", "last_updated_at")
    list_filter = ("check_type", "is_active", "created_at")
    search_fields = ("title", "url", "user__email")
    ordering = ("-last_updated_at",)
