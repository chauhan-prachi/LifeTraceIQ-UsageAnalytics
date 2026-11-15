from django.http import JsonResponse
from django.shortcuts import render

from .services import get_dashboard_data


def format_duration(seconds):
    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"

    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60

    if hours:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"


def dashboard(request):
    data = get_dashboard_data()

    data["total_label"] = format_duration(data["total_seconds"])
    data["productive_label"] = format_duration(data["productive_seconds"])
    data["distracting_label"] = format_duration(data["distracting_seconds"])

    total = data["total_seconds"] or 1

    data["productive_percent"] = round(
        data["productive_seconds"] * 100 / total
    )

    data["distracting_percent"] = round(
        data["distracting_seconds"] * 100 / total
    )

    category_labels = {
        "productive": "Productive",
        "social": "Social media",
        "entertainment": "Entertainment",
        "browsing": "Browsing",
        "other": "Other",
    }

    for row in data["category_rows"]:
        row["label"] = category_labels.get(
            row["category"],
            row["category"].title()
        )
        row["duration"] = format_duration(row["seconds"])

    for row in data["app_rows"]:
        row["duration"] = format_duration(row["seconds"])

    return render(request, "tracker/dashboard.html", data)


def summary_api(request):
    data = get_dashboard_data()

    return JsonResponse({
        "date": str(data["today"]),
        "total_seconds": data["total_seconds"],
        "productive_seconds": data["productive_seconds"],
        "distracting_seconds": data["distracting_seconds"],
        "top_apps": data["app_rows"],
        "categories": data["category_rows"],
    })