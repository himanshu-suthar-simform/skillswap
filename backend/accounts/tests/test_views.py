"""
Unit tests for accounts views.

This module contains comprehensive tests for all API views in the accounts app,
covering authentication, user management, and profile operations.
"""

import io

from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationViewTestCase(APITestCase):
    """Test cases for UserRegistrationView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:register")
        self.valid_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        }

    def test_register_user_with_valid_data(self):
        """Test registering a new user with valid data."""
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertTrue(user.check_password(self.valid_data["password"]))
        self.assertTrue(hasattr(user, "profile"))

    def test_register_user_with_profile_data(self):
        """Test registering user with profile data."""
        data = self.valid_data.copy()
        data["profile"] = {
            "bio": "Test bio",
            "location": "New York",
            "timezone": "America/New_York",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.first()
        self.assertEqual(user.profile.bio, "Test bio")
        self.assertEqual(user.profile.location, "New York")

    def test_register_user_with_profile_picture(self):
        """Test registering user with profile picture."""
        # Create a test image
        image = Image.new("RGB", (200, 200), color="red")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        data = self.valid_data.copy()
        data["profile"] = {
            "profile_picture": SimpleUploadedFile(
                "test.jpg",
                image_file.read(),
                content_type="image/jpeg",
            )
        }

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.first()
        self.assertIsNotNone(user.profile.profile_picture)

    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = self.valid_data.copy()
        data["password_confirm"] = "DifferentPass123!"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            email=self.valid_data["email"],
            username="existinguser",
            password="pass123",
        )

        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_weak_password(self):
        """Test registration fails with weak password."""
        data = self.valid_data.copy()
        data["password"] = "weak"
        data["password_confirm"] = "weak"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_missing_required_fields(self):
        """Test registration fails when required fields are missing."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_register_user_invalid_email(self):
        """Test registration fails with invalid email format."""
        data = self.valid_data.copy()
        data["email"] = "invalid-email"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_no_authentication_required(self):
        """Test that registration endpoint doesn't require authentication."""
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_sets_default_role(self):
        """Test that registered user has default USER role."""
        response = self.client.post(self.url, self.valid_data, format="json")

        user = User.objects.first()
        self.assertEqual(user.role, User.Role.USER)

    def test_register_user_creates_profile(self):
        """Test that profile is automatically created."""
        response = self.client.post(self.url, self.valid_data, format="json")

        user = User.objects.first()
        self.assertTrue(Profile.objects.filter(user=user).exists())


class CustomTokenObtainPairViewTestCase(APITestCase):
    """Test cases for CustomTokenObtainPairView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:token_obtain_pair")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="New York",
        )

    def test_obtain_token_with_valid_credentials(self):
        """Test obtaining token with valid credentials."""
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_obtain_token_includes_user_data(self):
        """Test that token response includes user data."""
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")

        user_data = response.data["user"]
        self.assertEqual(user_data["email"], self.user.email)
        self.assertEqual(user_data["username"], self.user.username)
        self.assertEqual(user_data["role"], self.user.role)

    def test_obtain_token_includes_profile_data(self):
        """Test that token response includes profile data."""
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")

        profile_data = response.data["user"]["profile"]
        self.assertEqual(profile_data["bio"], "Test bio")
        self.assertEqual(profile_data["location"], "New York")

    def test_obtain_token_with_invalid_credentials(self):
        """Test obtaining token fails with invalid credentials."""
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_with_inactive_user(self):
        """Test obtaining token fails for inactive user."""
        self.user.is_active = False
        self.user.save()

        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_with_nonexistent_user(self):
        """Test obtaining token fails for nonexistent user."""
        data = {
            "email": "nonexistent@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_missing_credentials(self):
        """Test obtaining token fails when credentials are missing."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_no_authentication_required(self):
        """Test that token endpoint doesn't require authentication."""
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomTokenRefreshViewTestCase(APITestCase):
    """Test cases for CustomTokenRefreshView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:token_refresh")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_refresh_token_with_valid_token(self):
        """Test refreshing token with valid refresh token."""
        data = {"refresh": str(self.refresh)}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_with_invalid_token(self):
        """Test refreshing token fails with invalid token."""
        data = {"refresh": "invalid-token"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_missing_token(self):
        """Test refreshing token fails when token is missing."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_no_authentication_required(self):
        """Test that refresh endpoint doesn't require authentication."""
        data = {"refresh": str(self.refresh)}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomTokenVerifyViewTestCase(APITestCase):
    """Test cases for CustomTokenVerifyView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:token_verify")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            is_active=True,
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        data = {"token": self.access_token}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        data = {"token": "invalid-token"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_missing_token(self):
        """Test verifying fails when token is missing."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_token_no_authentication_required(self):
        """Test that verify endpoint doesn't require authentication."""
        data = {"token": self.access_token}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserListViewTestCase(APITestCase):
    """Test cases for UserListView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:user_list")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            is_active=True,
        )
        Profile.objects.create(user=self.user)

        # Create additional test users
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="pass123",
            first_name="John",
            last_name="Doe",
            is_active=True,
        )
        Profile.objects.create(
            user=self.user2,
            location="New York",
            is_available=True,
        )

        self.user3 = User.objects.create_user(
            email="user3@example.com",
            username="user3",
            password="pass123",
            first_name="Jane",
            last_name="Smith",
            is_active=True,
        )
        Profile.objects.create(
            user=self.user3,
            location="San Francisco",
            is_available=False,
        )

        # Inactive user (should not appear in results)
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="pass123",
            is_active=False,
        )

        self.client.force_authenticate(user=self.user)

    def test_list_users_authenticated(self):
        """Test listing users when authenticated."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_list_users_unauthenticated(self):
        """Test listing users fails when not authenticated."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_only_active(self):
        """Test that only active users are listed."""
        response = self.client.get(self.url)

        user_ids = [user["id"] for user in response.data["results"]]
        self.assertIn(self.user.id, user_ids)
        self.assertIn(self.user2.id, user_ids)
        self.assertIn(self.user3.id, user_ids)
        self.assertNotIn(self.inactive_user.id, user_ids)

    def test_list_users_search_by_username(self):
        """Test searching users by username."""
        response = self.client.get(self.url, {"search": "user2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "user2")

    def test_list_users_search_by_email(self):
        """Test searching users by email."""
        response = self.client.get(self.url, {"search": "user2@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "user2@example.com")

    def test_list_users_search_by_first_name(self):
        """Test searching users by first name."""
        response = self.client.get(self.url, {"search": "John"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("John", response.data["results"][0]["full_name"])

    def test_list_users_search_by_last_name(self):
        """Test searching users by last name."""
        response = self.client.get(self.url, {"search": "Smith"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("Smith", response.data["results"][0]["last_name"])

    def test_list_users_filter_by_location(self):
        """Test filtering users by location."""
        response = self.client.get(self.url, {"location": "New York"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.user2.id)

    def test_list_users_filter_by_availability_true(self):
        """Test filtering users by availability (true)."""
        response = self.client.get(self.url, {"is_available": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include user and user2 (both available)
        user_ids = [user["id"] for user in response.data["results"]]
        self.assertIn(self.user2.id, user_ids)
        self.assertNotIn(self.user3.id, user_ids)

    def test_list_users_filter_by_availability_false(self):
        """Test filtering users by availability (false)."""
        response = self.client.get(self.url, {"is_available": "false"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_ids = [user["id"] for user in response.data["results"]]
        self.assertIn(self.user3.id, user_ids)

    def test_list_users_combined_filters(self):
        """Test combining multiple filters."""
        response = self.client.get(
            self.url,
            {"location": "New York", "is_available": "true"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.user2.id)

    def test_list_users_ordering(self):
        """Test that users are ordered by date_joined descending."""
        response = self.client.get(self.url)

        results = response.data["results"]
        # Most recent user should be first
        self.assertEqual(results[0]["id"], self.user3.id)

    def test_list_users_pagination(self):
        """Test that results are paginated."""
        response = self.client.get(self.url)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)


class UserDetailViewTestCase(APITestCase):
    """Test cases for UserDetailView."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="New York",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="pass123",
            is_active=True,
        )
        Profile.objects.create(user=self.other_user)

        self.url = reverse("accounts:user_detail", kwargs={"pk": self.other_user.id})
        self.client.force_authenticate(user=self.user)

    def test_get_user_detail_authenticated(self):
        """Test getting user detail when authenticated."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.other_user.id)
        self.assertEqual(response.data["email"], self.other_user.email)
        self.assertIn("profile", response.data)

    def test_get_user_detail_unauthenticated(self):
        """Test getting user detail fails when not authenticated."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_includes_profile(self):
        """Test that user detail includes profile information."""
        response = self.client.get(self.url)

        self.assertIn("profile", response.data)
        self.assertIsNotNone(response.data["profile"])

    def test_get_user_detail_nonexistent_user(self):
        """Test getting detail for nonexistent user returns 404."""
        url = reverse("accounts:user_detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_detail_inactive_user(self):
        """Test getting detail for inactive user returns 404."""
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="pass123",
            is_active=False,
        )

        url = reverse("accounts:user_detail", kwargs={"pk": inactive_user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_detail_includes_timestamps(self):
        """Test that user detail includes timestamp fields."""
        response = self.client.get(self.url)

        self.assertIn("date_joined", response.data)
        self.assertIn("last_login", response.data)


class CurrentUserViewTestCase(APITestCase):
    """Test cases for CurrentUserView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:current_user")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="New York",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_current_user_authenticated(self):
        """Test getting current user when authenticated."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_current_user_unauthenticated(self):
        """Test getting current user fails when not authenticated."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user_includes_profile(self):
        """Test that current user response includes profile."""
        response = self.client.get(self.url)

        self.assertIn("profile", response.data)
        self.assertEqual(response.data["profile"]["bio"], "Test bio")
        self.assertEqual(response.data["profile"]["location"], "New York")

    def test_get_current_user_returns_authenticated_user(self):
        """Test that endpoint returns the authenticated user's data."""
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="pass123",
            is_active=True,
        )

        # Even though other_user exists, should return self.user
        response = self.client.get(self.url)

        self.assertEqual(response.data["id"], self.user.id)
        self.assertNotEqual(response.data["id"], other_user.id)


class UserProfileUpdateViewTestCase(APITestCase):
    """Test cases for UserProfileUpdateView."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("accounts:profile_update")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Original bio",
            location="Original location",
        )
        self.client.force_authenticate(user=self.user)

    def test_update_profile_authenticated(self):
        """Test updating profile when authenticated."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "profile": {
                "bio": "Updated bio",
                "location": "Updated location",
            },
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertEqual(self.profile.location, "Updated location")

    def test_update_profile_unauthenticated(self):
        """Test updating profile fails when not authenticated."""
        self.client.force_authenticate(user=None)
        data = {"first_name": "Updated"}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_user_fields_only(self):
        """Test updating only user fields."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_update_profile_profile_fields_only(self):
        """Test updating only profile fields."""
        data = {
            "profile": {
                "bio": "Updated bio",
                "location": "Updated location",
            }
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertEqual(self.profile.location, "Updated location")

    def test_update_profile_with_profile_picture(self):
        """Test updating profile with profile picture."""
        # Create a test image
        image = Image.new("RGB", (200, 200), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        data = {
            "profile": {
                "profile_picture": SimpleUploadedFile(
                    "test.jpg",
                    image_file.read(),
                    content_type="image/jpeg",
                )
            }
        }

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.profile_picture)

    def test_update_profile_empty_first_name(self):
        """Test updating profile fails with empty first name."""
        data = {"first_name": "   "}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)

    def test_update_profile_empty_last_name(self):
        """Test updating profile fails with empty last name."""
        data = {"last_name": "   "}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)

    def test_update_profile_first_name_too_long(self):
        """Test updating profile fails when first name is too long."""
        data = {"first_name": "x" * 151}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)

    def test_update_profile_returns_complete_user_data(self):
        """Test that update returns complete user data."""
        data = {"first_name": "Updated"}

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("email", response.data)
        self.assertIn("profile", response.data)
        self.assertIn("date_joined", response.data)

    def test_update_profile_partial_update(self):
        """Test partial update of profile."""
        original_last_name = self.user.last_name
        original_location = self.profile.location

        data = {
            "first_name": "Updated",
            "profile": {"bio": "Updated bio"},
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, original_last_name)
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertEqual(self.profile.location, original_location)

    def test_update_profile_only_updates_own_profile(self):
        """Test that user can only update their own profile."""
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="pass123",
            is_active=True,
        )
        Profile.objects.create(user=other_user)

        data = {"first_name": "Updated"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only authenticated user was updated
        self.user.refresh_from_db()
        other_user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Updated")
        self.assertNotEqual(other_user.first_name, "Updated")

    def test_update_profile_availability_status(self):
        """Test updating availability status."""
        data = {
            "profile": {
                "is_available": False,
            }
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_available)

    def test_update_profile_timezone(self):
        """Test updating timezone."""
        data = {
            "profile": {
                "timezone": "America/Los_Angeles",
            }
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.timezone, "America/Los_Angeles")

    def test_update_profile_language_preference(self):
        """Test updating language preference."""
        data = {
            "profile": {
                "language_preference": "es",
            }
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.language_preference, "es")
