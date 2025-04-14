import datetime
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UrlItem
from .forms import BulkUrlAddForm

User = get_user_model()


class UrlManagerViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)
        self.list_url = reverse("url_manager:url_list")
        self.bulk_add_url = reverse("url_manager:url_bulk_add")

    def test_bulk_add_view_get(self):
        """Test GET request for bulk add view"""
        response = self.client.get(self.bulk_add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "url_manager/url_bulk_add.html")
        self.assertIsInstance(response.context["form"], BulkUrlAddForm)

    def test_bulk_add_view_post_success(self):
        """Test POST request for bulk add view with valid data"""
        urls_to_add = "https://example.com\nhttp://example.org"
        with patch(
            "url_manager.views.get_page_title", return_value="Mock Title"
        ) as mock_title, patch(
            "url_manager.views.check_url_update.delay"
        ) as mock_check, patch(
            "url_manager.views.update_thumbnail.delay"
        ) as mock_thumb:
            response = self.client.post(self.bulk_add_url, {"urls": urls_to_add})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)

        self.assertEqual(
            UrlItem.objects.filter(user=self.user).count(), 2
        )  # pylint: disable=no-member
        self.assertTrue(
            UrlItem.objects.filter(
                user=self.user, url="https://example.com"
            ).exists()  # pylint: disable=no-member
        )
        self.assertTrue(
            UrlItem.objects.filter(
                user=self.user, url="http://example.org"
            ).exists()  # pylint: disable=no-member
        )
        item1 = UrlItem.objects.get(
            user=self.user, url="https://example.com"
        )  # pylint: disable=no-member
        item2 = UrlItem.objects.get(
            user=self.user, url="http://example.org"
        )  # pylint: disable=no-member
        self.assertTrue(item1.title)
        self.assertTrue(item2.title)

    def test_bulk_add_view_post_empty(self):
        """Test POST request with empty URL list"""
        response = self.client.post(self.bulk_add_url, {"urls": ""})
        self.assertEqual(response.status_code, 200)  # Should re-render the form
        self.assertFormError(
            response, "form", "urls", "少なくとも1つのURLを入力してください。"
        )
        self.assertEqual(
            UrlItem.objects.filter(user=self.user).count(), 0
        )  # pylint: disable=no-member

    def test_bulk_add_view_post_invalid_and_duplicate(self):
        """Test POST request with invalid format and duplicate URLs"""
        UrlItem.objects.create(  # pylint: disable=no-member
            user=self.user, url="https://existing.com", title="Existing"
        )

        urls_to_add = "invalid-url\nhttps://existing.com\nhttp://newvalid.com"
        with patch(
            "url_manager.views.get_page_title", return_value="Mock Title"
        ) as mock_title, patch(
            "url_manager.views.check_url_update.delay"
        ) as mock_check, patch(
            "url_manager.views.update_thumbnail.delay"
        ) as mock_thumb:
            response = self.client.post(self.bulk_add_url, {"urls": urls_to_add})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)

        self.assertEqual(
            UrlItem.objects.filter(user=self.user).count(),
            2,  # pylint: disable=no-member
        )  # existing.com + newvalid.com
        self.assertTrue(
            UrlItem.objects.filter(
                user=self.user, url="http://newvalid.com"
            ).exists()  # pylint: disable=no-member
        )
        self.assertFalse(
            UrlItem.objects.filter(
                user=self.user, url="invalid-url"
            ).exists()  # pylint: disable=no-member
        )


class BulkUrlAddFormTestCase(TestCase):
    def test_valid_urls(self):
        form = BulkUrlAddForm(data={"urls": "https://example.com\nhttp://test.org"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["urls"], ["https://example.com", "http://test.org"]
        )

    def test_empty_urls(self):
        form = BulkUrlAddForm(data={"urls": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("urls", form.errors)
        self.assertEqual(
            form.errors["urls"], ["少なくとも1つのURLを入力してください。"]
        )  # Check custom validation message

    def test_urls_with_whitespace(self):
        form = BulkUrlAddForm(
            data={"urls": "  https://example.com  \n\n http://test.org \n "}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["urls"], ["https://example.com", "http://test.org"]
        )
