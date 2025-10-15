from django.db import models
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from .models import User
from .serializers import CustomTokenObtainPairSerializer
from .serializers import UserDetailSerializer
from .serializers import UserListSerializer
from .serializers import UserProfileUpdateSerializer
from .serializers import UserRegistrationSerializer


@extend_schema(
    tags=["Authentication"],
    auth=[],
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


@extend_schema(
    tags=["Users"],
    description="List all active users",
    parameters=[
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Search users by username, email, or full name",
        ),
        OpenApiParameter(
            name="location",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users by location",
        ),
        OpenApiParameter(
            name="is_available",
            type=bool,
            location=OpenApiParameter.QUERY,
            description="Filter users by availability status",
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="List of users",
            response=UserListSerializer(many=True),
        ),
    },
)
class UserListView(ListAPIView):
    """
    List all active users with optional filtering and search.

    This view provides a paginated list of all active users in the system.
    It supports:
    - Search by username, email, or full name
    - Filtering by location
    - Filtering by availability status

    The response is paginated and ordered by join date (newest first).
    Only basic user information and minimal profile details are included
    in the response to keep it lightweight.
    """

    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get the queryset of active users with optional filtering.

        Returns:
            QuerySet: Filtered queryset of active users
        """
        queryset = User.objects.filter(is_active=True)

        # Apply search filter
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search)
                | models.Q(email__icontains=search)
                | models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
            )

        # Filter by location
        location = self.request.query_params.get("location", "").strip()
        if location:
            queryset = queryset.filter(profile__location__icontains=location)

        # Filter by availability
        is_available = self.request.query_params.get("is_available")
        if is_available is not None:
            is_available = is_available.lower() == "true"
            queryset = queryset.filter(profile__is_available=is_available)

        return queryset.select_related("profile").order_by("-date_joined")


@extend_schema(
    tags=["Users"],
    description="Get detailed information about a specific user",
    responses={
        200: OpenApiResponse(
            description="User details retrieved successfully",
            response=UserDetailSerializer,
        ),
        404: OpenApiResponse(description="User not found"),
    },
)
class UserDetailView(RetrieveAPIView):
    """
    Retrieve detailed information about a specific user.

    This view provides comprehensive information about a user, including:
    - Basic user details (id, username, email, etc.)
    - Profile information
    - Join date and last login
    - Availability status

    Only active users can be retrieved through this endpoint.
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the user object.

        Returns:
            User: The requested user instance

        Raises:
            Http404: If user doesn't exist or is inactive
        """
        user = get_object_or_404(
            User.objects.select_related("profile"),
            id=self.kwargs["pk"],
            is_active=True,
        )
        return user


@extend_schema(
    tags=["Users"],
    description="Get current logged-in user's information",
    responses={
        200: OpenApiResponse(
            description="User information retrieved successfully",
            response=UserDetailSerializer,
        ),
    },
)
class CurrentUserView(RetrieveAPIView):
    """
    Retrieve detailed information about the currently logged-in user.

    This view returns comprehensive information about the authenticated user,
    including:
    - Basic user details
    - Complete profile information
    - Account status
    - Join date and last login
    """

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get the current user object.

        Returns:
            User: The current authenticated user instance
        """
        return self.request.user


@extend_schema(
    tags=["Users"],
    description="Update user profile information",
    request=UserProfileUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="Profile updated successfully",
            response=UserDetailSerializer,
        ),
        400: OpenApiResponse(description="Invalid data provided"),
    },
)
class UserProfileUpdateView(UpdateAPIView):
    """
    Update profile information for the currently logged-in user.

    This view handles updates to both User and Profile models in a single request.
    It supports:
    - Updating basic user information (first name, last name)
    - Updating profile fields (bio, location, etc.)
    - Uploading/updating profile picture

    The view accepts both JSON and multipart form data to handle file uploads.
    After successful update, returns the complete updated user information.
    """

    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        """
        Get the current user object.

        Returns:
            User: The current authenticated user instance
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Handle the update request.

        Args:
            request: The HTTP request

        Returns:
            Response: Updated user data or validation errors
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return complete user data after update
        return Response(
            UserDetailSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
