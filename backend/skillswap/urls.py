from django.contrib import admin
from django.urls import path

from .healthcheck import healthcheck

urlpatterns = [
    path("status", healthcheck, name="healthcheck"),
    path("admin/", admin.site.urls),
]
