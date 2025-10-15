from django.urls import path

from .views import CurrentUserView
from .views import CustomTokenObtainPairView
from .views import CustomTokenRefreshView
from .views import CustomTokenVerifyView
from .views import UserDetailView
from .views import UserListView
from .views import UserProfileUpdateView
from .views import UserRegistrationView

app_name = "accounts"

# Authentication endpoints
urlpatterns = [
    # User registration and authentication
    path("auth/register/", UserRegistrationView.as_view(), name="register"),
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    # User management endpoints
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/me/", CurrentUserView.as_view(), name="current_user"),
    path("users/me/profile/", UserProfileUpdateView.as_view(), name="profile_update"),
]
