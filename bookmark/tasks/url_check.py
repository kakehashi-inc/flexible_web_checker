import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from bookmark.models import UrlItem
from bookmark.utils import (
    check_rss_feed,
    check_html_standard,
    check_html_custom,
    take_screenshot,
)

logger = logging.getLogger(__name__)


@shared_task
def check_url_updates():
    """すべてのアクティブなURLの更新をチェックする"""
    logger.info("Starting URL update check task")

    url_items = UrlItem.objects.filter(is_active=True)

    for url_item in url_items:
        try:
            check_url_update.delay(url_item.id)
        except Exception as e:
            logger.error(f"Error scheduling check for URL {url_item.id}: {str(e)}")

    logger.info(f"Scheduled update checks for {url_items.count()} URLs")
    return True


@shared_task
def check_url_update(url_item_id):
    """特定のURLの更新をチェックする"""
    try:
        url_item = UrlItem.objects.get(id=url_item_id)

        if not url_item.is_active:
            return False

        logger.info(f"Checking updates for URL: {url_item.url}")

        url_item.last_checked_at = timezone.now()

        is_updated = False
        new_hash = url_item.last_content_hash

        try:
            if url_item.check_type == "RSS":
                is_updated, new_hash = check_rss_feed(
                    url_item.url, url_item.last_content_hash
                )
            elif url_item.check_type == "HTML_STANDARD":
                is_updated, new_hash = check_html_standard(
                    url_item.url, url_item.last_content_hash
                )
            elif url_item.check_type == "HTML_CUSTOM":
                selectors = (
                    url_item.html_selector.splitlines()
                    if url_item.html_selector
                    else []
                )
                condition = url_item.html_custom_condition or "OR"
                is_updated, new_hash = check_html_custom(
                    url_item.url, selectors, condition, url_item.last_content_hash
                )

            url_item.error_count = 0
            url_item.last_error_message = None

        except Exception as e:
            url_item.error_count += 1
            url_item.last_error_message = str(e)
            logger.error(f"Error checking URL {url_item.url}: {str(e)}")
            url_item.save()
            return False

        if is_updated:
            url_item.last_updated_at = timezone.now()
            url_item.last_content_hash = new_hash
            logger.info(f"URL updated: {url_item.url}")

            if not url_item.thumbnail:
                try:
                    screenshot_path = f"thumbnails/{url_item_id}.png"
                    full_path = f"{settings.MEDIA_ROOT}/{screenshot_path}"
                    take_screenshot(url_item.url, full_path)
                    url_item.thumbnail = screenshot_path
                except Exception as e:
                    logger.error(
                        f"Error taking screenshot for {url_item.url}: {str(e)}"
                    )

        url_item.save()
        return is_updated

    except UrlItem.DoesNotExist:
        logger.error(f"URL item with ID {url_item_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking URL {url_item_id}: {str(e)}")
        return False


@shared_task
def check_all_urls_task(user_id):
    """特定のユーザーのすべてのURLの更新をチェックする"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)

        logger.info(f"Starting URL update check for user ID: {user_id}")

        url_items = UrlItem.objects.filter(user=user, is_active=True)

        for url_item in url_items:
            try:
                check_url_update.delay(url_item.id)
            except Exception as e:
                logger.error(f"Error scheduling check for URL {url_item.id}: {str(e)}")

        logger.info(
            f"Scheduled update checks for {url_items.count()} URLs for user ID: {user_id}"
        )
        return True

    except Exception as e:
        logger.error(f"Error in check_all_urls_task: {str(e)}")
        return False
