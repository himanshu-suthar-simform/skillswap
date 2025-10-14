from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import CustomTokenObtainPairView
from .views import CustomTokenRefreshView
from .views import CustomTokenVerifyView
from .views import UserRegistrationView

app_name = "accounts"

# Authentication endpoints
auth_urlpatterns = [
    # User registration
    path("register/", UserRegistrationView.as_view(), name="register"),
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns = auth_urlpatterns

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
