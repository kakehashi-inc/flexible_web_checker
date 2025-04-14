from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import UrlItem

User = get_user_model()


class UrlListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
            nickname="Test User",
        )
        self.user.is_active = True  # Activate the user for login
        self.user.save()
        login_successful = self.client.login(
            username="testuser@example.com", password="password"
        )
        self.assertTrue(
            login_successful, "Test client login failed"
        )  # Add assertion to check login success

        self.url_categorized = UrlItem.objects.create(
            user=self.user, url="https://example.com/cat", title="Categorized"
        )

        self.url_uncategorized = UrlItem.objects.create(
            user=self.user, url="https://example.com/uncat", title="Uncategorized"
        )

    def test_all_tab_shows_all_urls(self):
        """Test that the 'all' tab shows all URLs for the user."""
        response = self.client.get(reverse("url_manager:url_list") + "?tab=all")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.url_categorized.title)
        self.assertContains(response, self.url_uncategorized.title)
        self.assertEqual(len(response.context["url_items"]), 2)

    def test_uncategorized_tab_filter_logic(self):
        """Test the basic filtering logic for uncategorized URLs (without needing Collection model fully)."""

        response_all = self.client.get(reverse("url_manager:url_list") + "?tab=all")
        response_uncat = self.client.get(
            reverse("url_manager:url_list") + "?tab=uncategorized"
        )

        self.assertEqual(response_all.status_code, 200)
        self.assertEqual(response_uncat.status_code, 200)

        self.assertEqual(response_all.context["active_tab"], "all")
        self.assertEqual(response_uncat.context["active_tab"], "uncategorized")

        self.assertIn("url_items", response_uncat.context)
