import logging
from celery import shared_task
from django.conf import settings
from bookmark.models import UrlItem
from bookmark.utils import take_screenshot

logger = logging.getLogger(__name__)


@shared_task
def update_thumbnails():
    """すべてのURLのサムネイルを更新する"""
    logger.info("Starting thumbnail update task")

    url_items = UrlItem.objects.filter(is_active=True)

    for url_item in url_items:
        try:
            update_thumbnail.delay(url_item.id)
        except Exception as e:
            logger.error(
                f"Error scheduling thumbnail update for URL {url_item.id}: {str(e)}"
            )

    logger.info(f"Scheduled thumbnail updates for {url_items.count()} URLs")
    return True


@shared_task
def update_thumbnail(url_item_id):
    """特定のURLのサムネイルを更新する"""
    try:
        url_item = UrlItem.objects.get(id=url_item_id)

        if not url_item.is_active:
            return False

        logger.info(f"Updating thumbnail for URL: {url_item.url}")

        try:
            screenshot_path = f"thumbnails/{url_item_id}.png"
            full_path = f"{settings.MEDIA_ROOT}/{screenshot_path}"
            take_screenshot(url_item.url, full_path)
            url_item.thumbnail = screenshot_path
            url_item.save()
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot for {url_item.url}: {str(e)}")
            return False

    except UrlItem.DoesNotExist:
        logger.error(f"URL item with ID {url_item_id} does not exist")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error updating thumbnail for URL {url_item_id}: {str(e)}"
        )
        return False
