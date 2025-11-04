import hashlib
import json
import logging
import os
import time
from io import BytesIO

import feedparser
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

logger = logging.getLogger(__name__)


def get_page_title(url):
    """URLからページタイトルを取得する"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else url
        return title.strip() if isinstance(title, str) else url
    except Exception as e:
        logger.warning(f"Failed to get title for {url}: {str(e)}")
        return url


def take_screenshot(url, output_path=None):
    """URLのスクリーンショットを取得する"""
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=390,844")  # iPhone 12 Pro size

        driver = webdriver.Firefox(options=options)
        driver.get(url)

        time.sleep(3)

        screenshot = driver.get_screenshot_as_png()

        driver.quit()

        img = Image.open(BytesIO(screenshot))

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PNG")
            return output_path
        else:
            img_io = BytesIO()
            img.save(img_io, "PNG")
            return img_io.getvalue()

    except WebDriverException as e:
        logger.error(f"Selenium error for {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Screenshot error for {url}: {str(e)}")
        return None


def check_rss_feed(url, last_content_hash):
    """RSSフィードの更新をチェックする"""
    feed = feedparser.parse(url)

    if not feed.entries:
        return False, last_content_hash

    newest_entry = feed.entries[0]

    content_to_hash = f"{newest_entry.get('id', '')}{newest_entry.get('title', '')}{newest_entry.get('published', '')}"
    current_hash = hashlib.md5(content_to_hash.encode()).hexdigest()

    is_updated = current_hash != last_content_hash

    return is_updated, current_hash


def check_html_standard(url, last_content_hash):
    """HTML標準の更新をチェックする"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.body.get_text() if soup.body else response.text

    current_hash = hashlib.md5(body.encode()).hexdigest()

    is_updated = current_hash != last_content_hash

    return is_updated, current_hash


def check_html_custom(url, selectors, condition, last_content_hash):
    """HTMLカスタムの更新をチェックする"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    current_contents = []
    for selector in selectors:
        selector = selector.strip()
        if not selector:
            continue

        elements = soup.select(selector)
        content = (
            "\n".join([el.get_text().strip() for el in elements]) if elements else ""
        )
        current_contents.append(content)

    previous_contents = []
    if last_content_hash:
        try:
            previous_contents = json.loads(last_content_hash)
        except json.JSONDecodeError:
            previous_contents = []

    if condition == "OR":
        is_updated = len(current_contents) != len(previous_contents) or any(
            c1 != c2 for c1, c2 in zip(current_contents, previous_contents)
        )
    else:  # 'AND'
        is_updated = len(current_contents) != len(previous_contents) or all(
            c1 != c2 for c1, c2 in zip(current_contents, previous_contents)
        )

    current_hash = json.dumps(current_contents)

    return is_updated, current_hash
