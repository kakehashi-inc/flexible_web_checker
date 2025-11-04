from django.contrib import admin
from bookmark.models import Collection, UrlItemCollection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "order", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "user__email")
    ordering = ("order", "name")


@admin.register(UrlItemCollection)
class UrlItemCollectionAdmin(admin.ModelAdmin):
    list_display = ("url_item", "collection", "added_at")
    list_filter = ("added_at",)
    search_fields = ("url_item__title", "collection__name")
    ordering = ("-added_at",)
