from django.contrib import admin
from django.urls import path
from tracker import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("api/summary/", views.summary_api, name="summary_api"),
]
