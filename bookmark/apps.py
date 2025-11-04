from django.apps import AppConfig


class BookmarkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookmark'
    verbose_name = 'Bookmark'

    def ready(self):
        """アプリケーションの準備が完了したときに呼ばれる"""
        # Admin設定を読み込む
        from bookmark.admin import user_accounts  # noqa
        from bookmark.admin import url_manager  # noqa
        from bookmark.admin import collection_manager  # noqa
        from bookmark.admin import core  # noqa
