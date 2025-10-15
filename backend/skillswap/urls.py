from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView

from .healthcheck import healthcheck

# API Documentation patterns
doc_patterns = [
    # API Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# API patterns
api_patterns = [
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("skillhub/", include("skillhub.urls", namespace="skillhub")),
]

# Main URL patterns
urlpatterns = [
    path("status/", healthcheck, name="healthcheck"),
    path("admin/", admin.site.urls),
    # Include API URLs under /api/v1/
    path("api/v1/", include(api_patterns)),
]

# Add documentation URLs based on environment
if settings.DEBUG or not settings.DEBUG:  # Available in both dev and prod
    urlpatterns.extend(doc_patterns)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
