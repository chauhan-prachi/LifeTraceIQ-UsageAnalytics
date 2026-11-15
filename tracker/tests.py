from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import UsageSample, ApplicationCategory
from .services import categorize_app, get_dashboard_data
from .views import format_duration


class CategorizeAppTests(TestCase):

    def test_productive_application(self):
        self.assertEqual(categorize_app("Code.exe"), "productive")

    def test_social_application(self):
        self.assertEqual(categorize_app("Instagram.exe"), "social")

    def test_entertainment_application(self):
        self.assertEqual(categorize_app("Spotify.exe"), "entertainment")

    def test_browsing_application(self):
        self.assertEqual(categorize_app("chrome.exe"), "browsing")

    def test_unknown_application(self):
        self.assertEqual(categorize_app("UnknownApp.exe"), "other")

    def test_custom_category_overrides_default_rule(self):
        ApplicationCategory.objects.create(
            app_name="chrome.exe",
            category="productive",
            is_active=True
        )

        self.assertEqual(categorize_app("chrome.exe"), "productive")

    def test_inactive_custom_category_is_ignored(self):
        ApplicationCategory.objects.create(
            app_name="chrome.exe",
            category="productive",
            is_active=False
        )

        self.assertEqual(categorize_app("chrome.exe"), "browsing")

    def test_custom_category_is_case_insensitive(self):
        ApplicationCategory.objects.create(
            app_name="MyCustomApp.exe",
            category="productive",
            is_active=True
        )

        self.assertEqual(
            categorize_app("mycustomapp.exe"),
            "productive"
        )


class FormatDurationTests(TestCase):

    def test_zero_seconds(self):
        self.assertEqual(format_duration(0), "0s")

    def test_seconds(self):
        self.assertEqual(format_duration(45), "45s")

    def test_minutes(self):
        self.assertEqual(format_duration(120), "2m")

    def test_hours_and_minutes(self):
        self.assertEqual(format_duration(3660), "1h 1m")

    def test_multiple_hours(self):
        self.assertEqual(format_duration(7320), "2h 2m")

class DashboardDataTests(TestCase):

    def setUp(self):
        now = timezone.now()

        UsageSample.objects.create(
            app_name="Code.exe",
            category="productive",
            captured_at=now,
            duration_seconds=120
        )

        UsageSample.objects.create(
            app_name="Instagram.exe",
            category="social",
            captured_at=now,
            duration_seconds=60
        )

        UsageSample.objects.create(
            app_name="Spotify.exe",
            category="entertainment",
            captured_at=now,
            duration_seconds=180
        )

        UsageSample.objects.create(
            app_name="Chrome.exe",
            category="browsing",
            captured_at=now,
            duration_seconds=240
        )

    def test_dashboard_total_seconds(self):
        data = get_dashboard_data()

        self.assertEqual(data["total_seconds"], 600)

    def test_productive_seconds(self):
        data = get_dashboard_data()

        self.assertEqual(data["productive_seconds"], 120)

    def test_distracting_seconds(self):
        data = get_dashboard_data()

        self.assertEqual(data["distracting_seconds"], 240)

    def test_category_breakdown(self):
        data = get_dashboard_data()

        categories = {
            row["category"]: row["seconds"]
            for row in data["category_rows"]
        }

        self.assertEqual(categories["productive"], 120)
        self.assertEqual(categories["social"], 60)
        self.assertEqual(categories["entertainment"], 180)
        self.assertEqual(categories["browsing"], 240)

    def test_top_applications(self):
        data = get_dashboard_data()

        self.assertEqual(data["app_rows"][0]["app_name"], "Chrome.exe")
        self.assertEqual(data["app_rows"][0]["seconds"], 240)

    def test_dashboard_ignores_previous_day_records(self):
        yesterday = timezone.now() - timedelta(days=1)

        UsageSample.objects.create(
            app_name="OldApp.exe",
            category="productive",
            captured_at=yesterday,
            duration_seconds=500
        )

        data = get_dashboard_data()

        self.assertEqual(data["total_seconds"], 600)


class DashboardViewTests(TestCase):

    def test_dashboard_page_loads(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_dashboard_contains_summary(self):
        response = self.client.get(reverse("dashboard"))

        self.assertIn("total_seconds", response.context)

    def test_summary_api_returns_success(self):
        response = self.client.get(reverse("summary_api"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"],
            "application/json"
        )

    def test_summary_api_contains_expected_fields(self):
        response = self.client.get(reverse("summary_api"))

        data = response.json()

        expected_fields = {
            "date",
            "total_seconds",
            "productive_seconds",
            "distracting_seconds",
            "top_apps",
            "categories"
        }

        self.assertEqual(set(data.keys()), expected_fields)

    def test_summary_api_returns_correct_totals(self):
        UsageSample.objects.create(
            app_name="Code.exe",
            category="productive",
            captured_at=timezone.now(),
            duration_seconds=300
        )

        response = self.client.get(reverse("summary_api"))

        data = response.json()

        self.assertEqual(data["total_seconds"], 300)
        self.assertEqual(data["productive_seconds"], 300)
        self.assertEqual(data["distracting_seconds"], 0)