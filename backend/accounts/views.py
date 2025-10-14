from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny

from .models import User
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
