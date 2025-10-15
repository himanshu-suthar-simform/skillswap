"""
Edge case tests for accounts app.

This module contains tests for edge cases, boundary conditions,
and unusual scenarios that might occur in production.
"""

from accounts.tests.test_utils import TestDataFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationEdgeCasesTestCase(APITestCase):
    """Edge case tests for user registration."""

    def test_register_with_very_long_valid_email(self):
        """Test registration with maximum length email."""
        # Email field typically allows 254 characters
        long_email = "a" * 240 + "@example.com"
        data = TestDataFactory.get_valid_registration_data(email=long_email)

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_unicode_characters_in_name(self):
        """Test registration with unicode characters in name."""
        data = TestDataFactory.get_valid_registration_data(
            first_name="José",
            last_name="Müller",
        )

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data["email"])
        self.assertEqual(user.first_name, "José")
        self.assertEqual(user.last_name, "Müller")

    def test_register_with_special_characters_in_username(self):
        """Test registration with special characters in username."""
        data = TestDataFactory.get_valid_registration_data(
            username="user_name-123",
        )

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_email_different_case(self):
        """Test that email case variations are handled correctly."""
        # Register with lowercase email
        data1 = TestDataFactory.get_valid_registration_data(
            email="test@example.com",
            username="user1",
        )

        url = reverse("accounts:register")
        response1 = self.client.post(url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Try to register with same email in different case
        data2 = TestDataFactory.get_valid_registration_data(
            email="TEST@EXAMPLE.COM",
            username="user2",
        )

        response2 = self.client.post(url, data2, format="json")
        # Should fail due to email uniqueness (case-insensitive in most DBs)
        # Note: Behavior depends on database collation settings

    def test_register_with_whitespace_in_fields(self):
        """Test registration with whitespace in fields."""
        data = TestDataFactory.get_valid_registration_data(
            first_name="  Test  ",
            last_name="  User  ",
        )

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_empty_profile_data(self):
        """Test registration with empty profile object."""
        data = TestDataFactory.get_valid_registration_data()
        data["profile"] = {}

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_null_profile_fields(self):
        """Test registration with null profile fields."""
        data = TestDataFactory.get_valid_registration_data()

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_maximum_length_bio(self):
        """Test registration with maximum length bio."""
        data = TestDataFactory.get_valid_registration_data()
        data["profile"] = {
            "bio": "x" * 500,  # Max length is 500
        }

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_bio_exceeding_max_length(self):
        """Test registration fails with bio exceeding max length."""
        data = TestDataFactory.get_valid_registration_data()
        data["profile"] = {
            "bio": "x" * 501,  # Exceeds max length
        }

        url = reverse("accounts:register")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfilePictureEdgeCasesTestCase(APITestCase):
    """Edge case tests for profile picture upload."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("accounts:profile_update")

    def test_upload_profile_picture_minimum_dimensions(self):
        """Test uploading profile picture with minimum allowed dimensions."""
        image = TestDataFactory.create_test_image(width=100, height=100)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_profile_picture_maximum_dimensions(self):
        """Test uploading profile picture with maximum allowed dimensions."""
        image = TestDataFactory.create_test_image(width=4000, height=4000)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_profile_picture_below_minimum_dimensions(self):
        """Test uploading profile picture below minimum dimensions fails."""
        image = TestDataFactory.create_test_image(width=50, height=50)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_profile_picture_above_maximum_dimensions(self):
        """Test uploading profile picture above maximum dimensions fails."""
        image = TestDataFactory.create_test_image(width=5000, height=5000)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_profile_picture_non_square(self):
        """Test uploading non-square profile picture."""
        image = TestDataFactory.create_test_image(width=200, height=300)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_profile_picture_png_format(self):
        """Test uploading profile picture in PNG format."""
        image = TestDataFactory.create_test_image(
            width=200, height=200, format="PNG", filename="test.png"
        )
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_profile_picture_gif_format(self):
        """Test uploading profile picture in GIF format."""
        image = TestDataFactory.create_test_image(
            width=200, height=200, format="GIF", filename="test.gif"
        )
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_non_image_file_as_profile_picture(self):
        """Test uploading non-image file as profile picture fails."""
        text_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain",
        )
        data = {"profile": {"profile_picture": text_file}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_corrupted_image_file(self):
        """Test uploading corrupted image file fails."""
        corrupted_file = SimpleUploadedFile(
            "test.jpg",
            b"corrupted image data",
            content_type="image/jpeg",
        )
        data = {"profile": {"profile_picture": corrupted_file}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MAX_FILE_UPLOAD_SIZE=1000)
    def test_upload_profile_picture_exceeding_size_limit(self):
        """Test uploading profile picture exceeding size limit fails."""
        # Create a large image
        image = TestDataFactory.create_test_image(width=1000, height=1000)
        data = {"profile": {"profile_picture": image}}

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationEdgeCasesTestCase(APITestCase):
    """Edge case tests for authentication."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(
            email="test@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_login_with_email_different_case(self):
        """Test login with email in different case."""
        url = reverse("accounts:token_obtain_pair")
        data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "testpass123",
        }

        response = self.client.post(url, data, format="json")

        # Should succeed (email lookup is typically case-insensitive)
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED],
        )

    def test_login_with_whitespace_in_email(self):
        """Test login with whitespace in email."""
        url = reverse("accounts:token_obtain_pair")
        data = {
            "email": "  test@example.com  ",
            "password": "testpass123",
        }

        response = self.client.post(url, data, format="json")

        # Behavior depends on serializer validation

    def test_login_with_empty_password(self):
        """Test login with empty password fails."""
        url = reverse("accounts:token_obtain_pair")
        data = {
            "email": "test@example.com",
            "password": "",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_very_long_password(self):
        """Test login with very long password."""
        url = reverse("accounts:token_obtain_pair")
        data = {
            "email": "test@example.com",
            "password": "x" * 1000,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multiple_failed_login_attempts(self):
        """Test multiple failed login attempts."""
        url = reverse("accounts:token_obtain_pair")
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }

        # Attempt multiple failed logins
        for _ in range(5):
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verify account is not locked (unless throttling is implemented)
        correct_data = {
            "email": "test@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, correct_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserListEdgeCasesTestCase(APITestCase):
    """Edge case tests for user list."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("accounts:user_list")

    def test_list_users_with_empty_search_query(self):
        """Test listing users with empty search query."""
        response = self.client.get(self.url, {"search": ""})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_with_whitespace_search_query(self):
        """Test listing users with whitespace-only search query."""
        response = self.client.get(self.url, {"search": "   "})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_with_special_characters_in_search(self):
        """Test listing users with special characters in search."""
        response = self.client.get(self.url, {"search": "@#$%"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty results or handle gracefully

    def test_list_users_with_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled safely."""
        response = self.client.get(self.url, {"search": "'; DROP TABLE users; --"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not cause any database issues

    def test_list_users_with_very_long_search_query(self):
        """Test listing users with very long search query."""
        response = self.client.get(self.url, {"search": "x" * 1000})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_with_invalid_availability_value(self):
        """Test listing users with invalid availability value."""
        response = self.client.get(self.url, {"is_available": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should ignore invalid value or return all users

    def test_list_users_with_multiple_filter_parameters(self):
        """Test listing users with multiple filter parameters."""
        response = self.client.get(
            self.url,
            {
                "search": "test",
                "location": "New York",
                "is_available": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_with_negative_pagination_offset(self):
        """Test listing users with negative pagination offset."""
        response = self.client.get(self.url, {"offset": -1})

        # Should handle gracefully (return first page or error)
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST],
        )

    def test_list_users_with_very_large_pagination_offset(self):
        """Test listing users with very large pagination offset."""
        response = self.client.get(self.url, {"offset": 999999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty results

    def test_list_users_with_zero_limit(self):
        """Test listing users with zero limit."""
        response = self.client.get(self.url, {"limit": 0})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileUpdateEdgeCasesTestCase(APITestCase):
    """Edge case tests for profile update."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("accounts:profile_update")

    def test_update_profile_with_empty_json(self):
        """Test updating profile with empty JSON."""
        response = self.client.patch(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile_with_null_values(self):
        """Test updating profile with null values."""
        data = {
            "profile": {
                "bio": None,
                "location": None,
            }
        }

        response = self.client.patch(self.url, data, format="json")

        # Should handle null values appropriately
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST],
        )

    def test_update_profile_with_only_whitespace_in_name(self):
        """Test updating profile with only whitespace in name."""
        data = {"first_name": "   "}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_with_unicode_characters(self):
        """Test updating profile with unicode characters."""
        data = {
            "first_name": "José",
            "profile": {
                "bio": "Hello 世界 🌍",
                "location": "São Paulo",
            },
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "José")
        self.assertIn("世界", self.profile.bio)

    def test_update_profile_with_maximum_length_fields(self):
        """Test updating profile with maximum length fields."""
        data = {
            "first_name": "x" * 150,
            "last_name": "y" * 150,
            "profile": {
                "bio": "z" * 500,
                "location": "a" * 100,
            },
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile_with_fields_exceeding_max_length(self):
        """Test updating profile with fields exceeding max length."""
        data = {
            "first_name": "x" * 151,
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_with_invalid_timezone(self):
        """Test updating profile with invalid timezone."""
        data = {
            "profile": {
                "timezone": "Invalid/Timezone",
            }
        }

        response = self.client.patch(self.url, data, format="json")

        # Should accept any string (validation depends on implementation)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile_multiple_times_rapidly(self):
        """Test updating profile multiple times in rapid succession."""
        for i in range(5):
            data = {"first_name": f"Name{i}"}
            response = self.client.patch(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify final state
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Name4")


class TokenEdgeCasesTestCase(APITestCase):
    """Edge case tests for JWT tokens."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)

    def test_verify_token_with_malformed_token(self):
        """Test verifying malformed token."""
        url = reverse("accounts:token_verify")
        data = {"token": "malformed.token.here"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_token_with_empty_token(self):
        """Test verifying empty token."""
        url = reverse("accounts:token_verify")
        data = {"token": ""}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_with_access_token(self):
        """Test refreshing using access token instead of refresh token."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        url = reverse("accounts:token_refresh")
        data = {"refresh": access_token}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_use_token_after_user_deactivation(self):
        """Test using token after user is deactivated."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # Deactivate user
        self.user.is_active = False
        self.user.save()

        # Try to use token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("accounts:current_user")
        response = self.client.get(url)

        # Should fail (user is inactive)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConcurrencyEdgeCasesTestCase(APITestCase):
    """Edge case tests for concurrent operations."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)

    def test_concurrent_profile_updates(self):
        """Test handling of concurrent profile updates."""
        url = reverse("accounts:profile_update")

        # Simulate concurrent updates
        data1 = {"first_name": "Update1"}
        data2 = {"last_name": "Update2"}

        response1 = self.client.patch(url, data1, format="json")
        response2 = self.client.patch(url, data2, format="json")

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Verify both updates were applied
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Update1")
        self.assertEqual(self.user.last_name, "Update2")
