from django.db import models


class UsageSample(models.Model):

    CATEGORY_CHOICES = [
        ("productive", "Productive"),
        ("social", "Social Media"),
        ("entertainment", "Entertainment"),
        ("browsing", "Browsing"),
        ("other", "Other"),
    ]

    app_name = models.CharField(max_length=160, db_index=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
        db_index=True
    )

    captured_at = models.DateTimeField(db_index=True)

    duration_seconds = models.PositiveSmallIntegerField(default=5)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["captured_at", "category"])
        ]

    def __str__(self):
        return f"{self.app_name} - {self.captured_at:%Y-%m-%d %H:%M}"


class ApplicationCategory(models.Model):

    app_name = models.CharField(
        max_length=160,
        unique=True
    )

    category = models.CharField(
        max_length=20,
        choices=UsageSample.CATEGORY_CHOICES,
        default="other"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["app_name"]
        verbose_name = "Application Category"
        verbose_name_plural = "Application Categories"

    def __str__(self):
        return f"{self.app_name} - {self.category}"