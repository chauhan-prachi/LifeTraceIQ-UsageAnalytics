from django.contrib import admin
from .models import UsageSample, ApplicationCategory


@admin.register(UsageSample)
class UsageSampleAdmin(admin.ModelAdmin):
    list_display = ("app_name", "category", "duration_seconds", "captured_at")
    list_filter = ("category", "captured_at")
    search_fields = ("app_name",)
    date_hierarchy = "captured_at"


@admin.register(ApplicationCategory)
class ApplicationCategoryAdmin(admin.ModelAdmin):
    list_display = ("app_name", "category", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("app_name",)
    list_editable = ("category", "is_active")