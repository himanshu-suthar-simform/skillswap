from django.contrib import admin
from django.urls import include, path

from .healthcheck import healthcheck

urlpatterns = [
    path("status", healthcheck, name="healthcheck"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("admin/", admin.site.urls),
]
