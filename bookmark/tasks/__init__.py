# Celeryタスクを自動検出させるために明示的にインポート
from bookmark.tasks.url_check import (  # noqa
    check_url_updates,
    check_url_update,
    check_all_urls_task,
)
from bookmark.tasks.thumbnail import (  # noqa
    update_thumbnails,
    update_thumbnail,
)
