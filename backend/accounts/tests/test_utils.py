"""
Utility functions and helpers for accounts tests.

This module provides reusable test utilities, fixtures, and helper functions
to reduce code duplication and improve test maintainability.
"""

import io
from typing import Dict
from typing import Optional

from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

User = get_user_model()


class TestDataFactory:
    """Factory class for creating test data."""

    @staticmethod
    def create_user(
        email: str = "testuser@example.com",
        username: str = "testuser",
        password: str = "testpass123",
        first_name: str = "Test",
        last_name: str = "User",
        is_active: bool = True,
        role: str = User.Role.USER,
        **kwargs,
    ) -> User:
        """
        Create a test user with default or custom values.

        Args:
            email: User email
            username: Username
            password: User password
            first_name: First name
            last_name: Last name
            is_active: Active status
            role: User role
            **kwargs: Additional user fields

        Returns:
            User: Created user instance
        """
        user_data = {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": is_active,
            "role": role,
            **kwargs,
        }
        user = User.objects.create_user(password=password, **user_data)
        return user

    @staticmethod
    def create_profile(
        user: User,
        bio: str = "",
        location: str = "",
        timezone: str = "UTC",
        language_preference: str = "en",
        is_available: bool = True,
        **kwargs,
    ) -> Profile:
        """
        Create a test profile for a user.

        Args:
            user: User instance
            bio: Profile bio
            location: User location
            timezone: User timezone
            language_preference: Preferred language
            is_available: Availability status
            **kwargs: Additional profile fields

        Returns:
            Profile: Created profile instance
        """
        profile_data = {
            "user": user,
            "bio": bio,
            "location": location,
            "timezone": timezone,
            "language_preference": language_preference,
            "is_available": is_available,
            **kwargs,
        }
        profile = Profile.objects.create(**profile_data)
        return profile

    @staticmethod
    def create_test_image(
        width: int = 200,
        height: int = 200,
        color: str = "red",
        format: str = "JPEG",
        filename: str = "test.jpg",
    ) -> SimpleUploadedFile:
        """
        Create a test image file for upload testing.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            color: Image color
            format: Image format (JPEG, PNG, etc.)
            filename: Filename for the uploaded file

        Returns:
            SimpleUploadedFile: Test image file
        """
        image = Image.new("RGB", (width, height), color=color)
        image_file = io.BytesIO()
        image.save(image_file, format)
        image_file.seek(0)

        content_type_map = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
        }

        return SimpleUploadedFile(
            filename,
            image_file.read(),
            content_type=content_type_map.get(format, "image/jpeg"),
        )

    @staticmethod
    def get_valid_registration_data(
        email: str = "newuser@example.com",
        username: str = "newuser",
        password: str = "StrongPass123!",
        first_name: str = "New",
        last_name: str = "User",
        include_profile: bool = False,
    ) -> Dict:
        """
        Get valid registration data for testing.

        Args:
            email: User email
            username: Username
            password: Password
            first_name: First name
            last_name: Last name
            include_profile: Whether to include profile data

        Returns:
            Dict: Registration data
        """
        data = {
            "email": email,
            "username": username,
            "password": password,
            "password_confirm": password,
            "first_name": first_name,
            "last_name": last_name,
        }

        if include_profile:
            data["profile"] = {
                "bio": "Test bio",
                "location": "Test location",
                "timezone": "UTC",
                "language_preference": "en",
            }

        return data

    @staticmethod
    def get_valid_login_data(
        email: str = "testuser@example.com",
        password: str = "testpass123",
    ) -> Dict:
        """
        Get valid login data for testing.

        Args:
            email: User email
            password: Password

        Returns:
            Dict: Login data
        """
        return {
            "email": email,
            "password": password,
        }

    @staticmethod
    def get_valid_profile_update_data(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        language_preference: Optional[str] = None,
        is_available: Optional[bool] = None,
    ) -> Dict:
        """
        Get valid profile update data for testing.

        Args:
            first_name: First name
            last_name: Last name
            bio: Bio
            location: Location
            timezone: Timezone
            language_preference: Language preference
            is_available: Availability status

        Returns:
            Dict: Profile update data
        """
        data = {}

        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name

        profile_data = {}
        if bio is not None:
            profile_data["bio"] = bio
        if location is not None:
            profile_data["location"] = location
        if timezone is not None:
            profile_data["timezone"] = timezone
        if language_preference is not None:
            profile_data["language_preference"] = language_preference
        if is_available is not None:
            profile_data["is_available"] = is_available

        if profile_data:
            data["profile"] = profile_data

        return data


class AssertionHelpers:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_user_data_matches(test_case, user_data: Dict, user: User):
        """
        Assert that user data matches user instance.

        Args:
            test_case: TestCase instance
            user_data: Dictionary of user data
            user: User instance
        """
        test_case.assertEqual(user_data.get("id"), user.id)
        test_case.assertEqual(user_data.get("email"), user.email)
        test_case.assertEqual(user_data.get("username"), user.username)

    @staticmethod
    def assert_profile_data_matches(test_case, profile_data: Dict, profile: Profile):
        """
        Assert that profile data matches profile instance.

        Args:
            test_case: TestCase instance
            profile_data: Dictionary of profile data
            profile: Profile instance
        """
        if "bio" in profile_data:
            test_case.assertEqual(profile_data["bio"], profile.bio)
        if "location" in profile_data:
            test_case.assertEqual(profile_data["location"], profile.location)
        if "timezone" in profile_data:
            test_case.assertEqual(profile_data["timezone"], profile.timezone)
        if "language_preference" in profile_data:
            test_case.assertEqual(
                profile_data["language_preference"], profile.language_preference
            )
        if "is_available" in profile_data:
            test_case.assertEqual(profile_data["is_available"], profile.is_available)

    @staticmethod
    def assert_response_has_keys(test_case, response_data: Dict, keys: list):
        """
        Assert that response data contains all specified keys.

        Args:
            test_case: TestCase instance
            response_data: Response data dictionary
            keys: List of expected keys
        """
        for key in keys:
            test_case.assertIn(key, response_data, f"Key '{key}' not found in response")

    @staticmethod
    def assert_validation_error(test_case, response_data: Dict, field: str):
        """
        Assert that response contains validation error for specific field.

        Args:
            test_case: TestCase instance
            response_data: Response data dictionary
            field: Field name that should have error
        """
        test_case.assertIn(
            field, response_data, f"Validation error for '{field}' not found"
        )


def create_authenticated_client(user: User):
    """
    Create an authenticated API client for testing.

    Args:
        user: User to authenticate

    Returns:
        APIClient: Authenticated client
    """
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_jwt_token(user: User) -> Dict[str, str]:
    """
    Create JWT tokens for a user.

    Args:
        user: User instance

    Returns:
        Dict: Dictionary with 'access' and 'refresh' tokens
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def get_auth_header(token: str) -> Dict[str, str]:
    """
    Get authorization header for JWT token.

    Args:
        token: JWT access token

    Returns:
        Dict: Authorization header
    """
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
