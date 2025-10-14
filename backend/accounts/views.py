from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from .models import User
from .serializers import CustomTokenObtainPairSerializer
from .serializers import UserRegistrationSerializer


@extend_schema(
    tags=["Authentication"],
    description="Register a new user account",
    responses={
        201: OpenApiResponse(
            description="User successfully registered",
            response=UserRegistrationSerializer,
        ),
        400: OpenApiResponse(
            description="Bad request (validation error)",
        ),
    },
)
class UserRegistrationView(CreateAPIView):
    """
    API endpoint for user registration.

    This view handles the creation of new user accounts with associated profiles.
    It automatically:
    1. Creates a new user account
    2. Creates an associated profile
    3. Sets appropriate role and permissions
    4. Validates all input data
    5. Handles profile picture upload

    Permissions:
    - AllowAny: This endpoint is publicly accessible

    Request Format:
    This endpoint accepts both JSON and multipart form data.

    For JSON (without profile picture):
    ```json
    {
        "email": "user@example.com",
        "username": "username",
        "password": "strong_password",
        "password_confirm": "strong_password",
        "first_name": "John",
        "last_name": "Doe",
        "profile": {
            "bio": "Optional bio",
            "phone_number": "Optional phone",
            "location": "Optional location",
            "timezone": "UTC",
            "language_preference": "en"
        }
    }
    ```

    For multipart form data (with profile picture):
    - Use form-data with the same fields as above
    - Add profile_picture as a file upload field

    Notes:
    - All profile fields are optional
    - Profile picture must be a valid image file (JPG, JPEG, PNG, GIF)
    - Maximum file size: 5MB
    - Minimum image dimensions: 100x100 pixels
    - Maximum image dimensions: 4000x4000 pixels
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        """
        Add request to serializer context for generating absolute URLs.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@extend_schema(
    tags=["Authentication"],
    description="Get JWT tokens (access and refresh) by providing credentials",
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated. Returns access token, refresh token and user details."
        ),
        401: OpenApiResponse(description="Invalid credentials"),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view that uses our custom serializer.

    Takes a set of user credentials and returns an access and refresh JSON web
    token pair along with user details to prove the authentication of those credentials.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def get_serializer_context(self):
        """Add request to serializer context for absolute URLs."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@extend_schema(
    tags=["Authentication"],
    description="Refresh access token using refresh token",
    responses={
        200: OpenApiResponse(
            description="Token successfully refreshed. Returns new access token."
        ),
        401: OpenApiResponse(description="Invalid or expired refresh token"),
    },
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view.

    Takes a refresh type JSON web token and returns an access type JSON web token
    if the refresh token is valid. Also handles token rotation if enabled.
    """


@extend_schema(
    tags=["Authentication"],
    description="Verify token validity",
    responses={
        200: OpenApiResponse(description="Token is valid"),
        401: OpenApiResponse(description="Token is invalid or expired"),
    },
)
class CustomTokenVerifyView(TokenVerifyView):
    """
    Custom token verify view.

    Takes a token and indicates if it is valid. This view provides no
    additional information about a token's validity.
    """
