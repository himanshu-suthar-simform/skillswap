from django.urls import path

from .views import CustomTokenObtainPairView
from .views import CustomTokenRefreshView
from .views import CustomTokenVerifyView
from .views import UserRegistrationView

app_name = "accounts"

# Authentication endpoints
urlpatterns = [
    # User registration
    path("auth/register/", UserRegistrationView.as_view(), name="register"),
    # JWT Token endpoints
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
]
