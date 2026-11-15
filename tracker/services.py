from datetime import datetime, time, timedelta

from django.db.models import Sum
from django.utils import timezone

from .models import UsageSample, ApplicationCategory


CATEGORY_RULES = {
    "productive": [
        "code",
        "pycharm",
        "visual studio",
        "notepad++",
        "word",
        "excel",
        "powerpoint",
        "terminal",
        "powershell",
    ],
    "social": [
        "instagram",
        "facebook",
        "whatsapp",
        "telegram",
        "discord",
        "snapchat",
        "x.exe",
    ],
    "entertainment": [
        "youtube",
        "netflix",
        "spotify",
        "vlc",
        "steam",
        "prime video",
    ],
    "browsing": [
        "chrome",
        "msedge",
        "firefox",
        "brave",
        "opera",
    ],
}


def categorize_app(app_name):

    value = app_name.strip()

    custom_category = (
        ApplicationCategory.objects
        .filter(app_name__iexact=value, is_active=True)
        .values_list("category", flat=True)
        .first()
    )

    if custom_category:
        return custom_category

    value = value.lower()

    for category, keywords in CATEGORY_RULES.items():

        if any(keyword in value for keyword in keywords):
            return category

    return "other"


def get_dashboard_data():

    today = timezone.localdate()

    start = timezone.make_aware(
        datetime.combine(today, time.min)
    )

    end = start + timedelta(days=1)

    samples = UsageSample.objects.filter(
        captured_at__gte=start,
        captured_at__lt=end
    )

    total_seconds = (
        samples.aggregate(total=Sum("duration_seconds"))["total"] or 0
    )

    category_rows = list(
        samples.values("category")
        .annotate(seconds=Sum("duration_seconds"))
        .order_by("-seconds")
    )

    app_rows = list(
        samples.values("app_name")
        .annotate(seconds=Sum("duration_seconds"))
        .order_by("-seconds")[:8]
    )

    productive = sum(
        row["seconds"]
        for row in category_rows
        if row["category"] == "productive"
    )

    distracting = sum(
        row["seconds"]
        for row in category_rows
        if row["category"] in ["social", "entertainment"]
    )

    return {
        "today": today,
        "total_seconds": total_seconds,
        "productive_seconds": productive,
        "distracting_seconds": distracting,
        "category_rows": category_rows,
        "app_rows": app_rows,
    }