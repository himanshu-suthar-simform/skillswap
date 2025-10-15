"""
Unit tests for accounts serializers.

This module contains comprehensive tests for all serializers in the accounts app,
covering validation, serialization, deserialization, and edge cases.
"""

import io

from accounts.models import Profile
from accounts.serializers import CustomTokenObtainPairSerializer
from accounts.serializers import ProfileSerializer
from accounts.serializers import UserBasicSerializer
from accounts.serializers import UserDetailSerializer
from accounts.serializers import UserListSerializer
from accounts.serializers import UserProfileUpdateSerializer
from accounts.serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from PIL import Image
from rest_framework.test import APIRequestFactory

User = get_user_model()


class UserBasicSerializerTestCase(TestCase):
    """Test cases for UserBasicSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.profile = Profile.objects.create(user=self.user)
        self.factory = APIRequestFactory()

    def test_serialize_user_basic_info(self):
        """Test serializing basic user information."""
        serializer = UserBasicSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["full_name"], "Test User")
        self.assertIn("profile_picture_url", data)
        self.assertIn("is_active", data)

    def test_full_name_with_complete_name(self):
        """Test full_name field with complete first and last name."""
        serializer = UserBasicSerializer(self.user)
        self.assertEqual(serializer.data["full_name"], "Test User")

    def test_full_name_fallback_to_username(self):
        """Test full_name falls back to username when name is empty."""
        user = User.objects.create_user(
            email="noname@example.com",
            username="noname",
            password="pass123",
            first_name="",
            last_name="",
        )
        serializer = UserBasicSerializer(user)
        self.assertEqual(serializer.data["full_name"], "noname")

    def test_profile_picture_url_when_exists(self):
        """Test profile_picture_url when profile picture exists."""
        # Create a test image
        image = Image.new("RGB", (100, 100), color="red")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        self.profile.profile_picture.save(
            "test.jpg",
            SimpleUploadedFile(
                "test.jpg", image_file.read(), content_type="image/jpeg"
            ),
        )

        serializer = UserBasicSerializer(self.user)
        self.assertIsNotNone(serializer.data["profile_picture_url"])
        self.assertIn("test", serializer.data["profile_picture_url"])

    def test_profile_picture_url_when_not_exists(self):
        """Test profile_picture_url when profile picture doesn't exist."""
        serializer = UserBasicSerializer(self.user)
        self.assertIsNone(serializer.data["profile_picture_url"])

    def test_profile_picture_url_when_no_profile(self):
        """Test profile_picture_url when user has no profile."""
        user = User.objects.create_user(
            email="noprofile@example.com",
            username="noprofile",
            password="pass123",
        )
        serializer = UserBasicSerializer(user)
        self.assertIsNone(serializer.data["profile_picture_url"])

    def test_all_fields_are_read_only(self):
        """Test that all fields are read-only."""
        serializer = UserBasicSerializer()
        for field_name in serializer.Meta.fields:
            field = serializer.fields[field_name]
            self.assertTrue(field.read_only)


class ProfileSerializerTestCase(TestCase):
    """Test cases for ProfileSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
        )
        self.profile = Profile.objects.create(user=self.user)
        self.factory = APIRequestFactory()

    def test_serialize_profile(self):
        """Test serializing profile data."""
        self.profile.bio = "Test bio"
        self.profile.location = "New York"
        self.profile.save()

        request = self.factory.get("/")
        serializer = ProfileSerializer(self.profile, context={"request": request})
        data = serializer.data

        self.assertEqual(data["bio"], "Test bio")
        self.assertEqual(data["location"], "New York")
        self.assertIn("profile_picture_url", data)
        self.assertNotIn("profile_picture", data)  # write_only field

    def test_deserialize_profile(self):
        """Test deserializing profile data."""
        data = {
            "bio": "New bio",
            "location": "San Francisco",
            "timezone": "America/Los_Angeles",
            "language_preference": "en",
            "is_available": True,
        }
        serializer = ProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["bio"], "New bio")

    def test_profile_picture_url_with_request_context(self):
        """Test profile_picture_url generation with request context."""
        # Create a test image
        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        self.profile.profile_picture.save(
            "test.jpg",
            SimpleUploadedFile(
                "test.jpg", image_file.read(), content_type="image/jpeg"
            ),
        )

        request = self.factory.get("/")
        serializer = ProfileSerializer(self.profile, context={"request": request})

        self.assertIsNotNone(serializer.data["profile_picture_url"])
        self.assertIn("http://", serializer.data["profile_picture_url"])

    def test_profile_picture_url_without_request_context(self):
        """Test profile_picture_url without request context."""
        serializer = ProfileSerializer(self.profile)
        self.assertIsNone(serializer.data["profile_picture_url"])

    def test_validate_profile_picture_valid_image(self):
        """Test validating a valid profile picture."""
        image = Image.new("RGB", (200, 200), color="green")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg",
        )

        serializer = ProfileSerializer()
        validated_file = serializer.validate_profile_picture(uploaded_file)
        self.assertIsNotNone(validated_file)

    @override_settings(MAX_FILE_UPLOAD_SIZE=100)
    def test_validate_profile_picture_file_too_large(self):
        """Test validating profile picture that exceeds size limit."""
        image = Image.new("RGB", (200, 200), color="red")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg",
        )

        serializer = ProfileSerializer()
        with self.assertRaises(Exception) as context:
            serializer.validate_profile_picture(uploaded_file)

        self.assertIn("5MB", str(context.exception))

    def test_validate_profile_picture_invalid_extension(self):
        """Test validating profile picture with invalid extension."""
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain",
        )

        serializer = ProfileSerializer()
        with self.assertRaises(Exception) as context:
            serializer.validate_profile_picture(uploaded_file)

        self.assertIn("JPG, JPEG, PNG and GIF", str(context.exception))

    def test_validate_profile_picture_dimensions_too_small(self):
        """Test validating profile picture with dimensions too small."""
        image = Image.new("RGB", (50, 50), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg",
        )

        serializer = ProfileSerializer()
        with self.assertRaises(Exception) as context:
            serializer.validate_profile_picture(uploaded_file)

        self.assertIn("100x100", str(context.exception))

    def test_validate_profile_picture_dimensions_too_large(self):
        """Test validating profile picture with dimensions too large."""
        image = Image.new("RGB", (5000, 5000), color="yellow")
        image_file = io.BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg",
        )

        serializer = ProfileSerializer()
        with self.assertRaises(Exception) as context:
            serializer.validate_profile_picture(uploaded_file)

        self.assertIn("4000x4000", str(context.exception))

    def test_validate_profile_picture_none_value(self):
        """Test validating None profile picture."""
        serializer = ProfileSerializer()
        result = serializer.validate_profile_picture(None)
        self.assertIsNone(result)

    def test_all_profile_fields_optional(self):
        """Test that all profile fields are optional."""
        serializer = ProfileSerializer(data={})
        self.assertTrue(serializer.is_valid())


class UserRegistrationSerializerTestCase(TestCase):
    """Test cases for UserRegistrationSerializer."""

    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        }

    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertTrue(user.check_password(self.valid_data["password"]))
        self.assertEqual(user.role, User.Role.USER)
        self.assertTrue(hasattr(user, "profile"))

    def test_create_user_with_profile_data(self):
        """Test creating user with profile data."""
        data = self.valid_data.copy()
        data["profile"] = {
            "bio": "Test bio",
            "location": "New York",
            "timezone": "America/New_York",
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.profile.bio, "Test bio")
        self.assertEqual(user.profile.location, "New York")
        self.assertEqual(user.profile.timezone, "America/New_York")

    def test_password_mismatch(self):
        """Test validation fails when passwords don't match."""
        data = self.valid_data.copy()
        data["password_confirm"] = "DifferentPass123!"

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_duplicate_email(self):
        """Test validation fails with duplicate email."""
        User.objects.create_user(
            email=self.valid_data["email"],
            username="existinguser",
            password="pass123",
        )

        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_weak_password(self):
        """Test validation fails with weak password."""
        data = self.valid_data.copy()
        data["password"] = "weak"
        data["password_confirm"] = "weak"

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        serializer = UserRegistrationSerializer(data={})
        self.assertFalse(serializer.is_valid())

        self.assertIn("email", serializer.errors)
        self.assertIn("username", serializer.errors)
        self.assertIn("password", serializer.errors)
        self.assertIn("first_name", serializer.errors)
        self.assertIn("last_name", serializer.errors)

    def test_password_not_in_response(self):
        """Test that password is not included in serialized data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        serializer = UserRegistrationSerializer(user)
        self.assertNotIn("password", serializer.data)
        self.assertNotIn("password_confirm", serializer.data)

    def test_id_is_read_only(self):
        """Test that id field is read-only."""
        data = self.valid_data.copy()
        data["id"] = 999

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertNotEqual(user.id, 999)

    def test_email_validation(self):
        """Test email format validation."""
        data = self.valid_data.copy()
        data["email"] = "invalid-email"

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class CustomTokenObtainPairSerializerTestCase(TestCase):
    """Test cases for CustomTokenObtainPairSerializer."""

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
        self.factory = APIRequestFactory()

    def test_token_generation_with_valid_credentials(self):
        """Test token generation with valid credentials."""
        request = self.factory.post("/")
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        serializer = CustomTokenObtainPairSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())

        token_data = serializer.validated_data

        self.assertIn("access", token_data)
        self.assertIn("refresh", token_data)
        self.assertIn("user", token_data)

    def test_token_includes_user_information(self):
        """Test that token response includes user information."""
        request = self.factory.post("/")
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        serializer = CustomTokenObtainPairSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())

        token_data = serializer.validated_data
        user_data = token_data["user"]

        self.assertEqual(user_data["id"], self.user.id)
        self.assertEqual(user_data["email"], self.user.email)
        self.assertEqual(user_data["username"], self.user.username)
        self.assertEqual(user_data["role"], self.user.role)

    def test_token_includes_profile_information(self):
        """Test that token response includes profile information."""
        request = self.factory.post("/")
        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        serializer = CustomTokenObtainPairSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())

        token_data = serializer.validated_data
        profile_data = token_data["user"]["profile"]

        self.assertEqual(profile_data["bio"], "Test bio")
        self.assertEqual(profile_data["location"], "New York")

    def test_token_generation_with_invalid_credentials(self):
        """Test token generation fails with invalid credentials."""
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_token_generation_with_inactive_user(self):
        """Test token generation fails for inactive user."""
        self.user.is_active = False
        self.user.save()

        data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class UserDetailSerializerTestCase(TestCase):
    """Test cases for UserDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="New York",
        )

    def test_serialize_user_detail(self):
        """Test serializing detailed user information."""
        serializer = UserDetailSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertIn("profile", data)
        self.assertIn("date_joined", data)
        self.assertIn("last_login", data)

    def test_profile_nested_in_user_detail(self):
        """Test that profile is properly nested in user detail."""
        serializer = UserDetailSerializer(self.user)
        profile_data = serializer.data["profile"]

        self.assertEqual(profile_data["bio"], "Test bio")
        self.assertEqual(profile_data["location"], "New York")

    def test_all_fields_are_read_only(self):
        """Test that all fields are read-only."""
        serializer = UserDetailSerializer()
        for field_name in serializer.Meta.fields:
            field = serializer.fields[field_name]
            if field_name != "profile":  # profile is a nested serializer
                self.assertTrue(field.read_only)


class UserProfileUpdateSerializerTestCase(TestCase):
    """Test cases for UserProfileUpdateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_update_user_basic_info(self):
        """Test updating user basic information."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, "Name")

    def test_update_profile_info(self):
        """Test updating profile information."""
        data = {
            "profile": {
                "bio": "Updated bio",
                "location": "San Francisco",
            }
        }

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.profile.bio, "Updated bio")
        self.assertEqual(updated_user.profile.location, "San Francisco")

    def test_update_both_user_and_profile(self):
        """Test updating both user and profile in single request."""
        data = {
            "first_name": "Updated",
            "profile": {
                "bio": "Updated bio",
            },
        }

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.profile.bio, "Updated bio")

    def test_validate_empty_first_name(self):
        """Test validation fails with empty first name."""
        data = {"first_name": "   "}

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_validate_empty_last_name(self):
        """Test validation fails with empty last name."""
        data = {"last_name": "   "}

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("last_name", serializer.errors)

    def test_validate_first_name_too_long(self):
        """Test validation fails when first name exceeds max length."""
        data = {"first_name": "x" * 151}

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_validate_last_name_too_long(self):
        """Test validation fails when last name exceeds max length."""
        data = {"last_name": "x" * 151}

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("last_name", serializer.errors)

    def test_partial_update(self):
        """Test partial update works correctly."""
        original_last_name = self.user.last_name
        data = {"first_name": "Updated"}

        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, original_last_name)


class UserListSerializerTestCase(TestCase):
    """Test cases for UserListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            location="New York",
            is_available=True,
        )

    def test_serialize_user_list(self):
        """Test serializing user for list view."""
        serializer = UserListSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["email"], self.user.email)
        self.assertIn("profile", data)
        self.assertIn("date_joined", data)

    def test_profile_minimal_info_in_list(self):
        """Test that only minimal profile info is included in list."""
        serializer = UserListSerializer(self.user)
        profile_data = serializer.data["profile"]

        self.assertEqual(profile_data["location"], "New York")
        self.assertEqual(profile_data["is_available"], True)
        self.assertEqual(len(profile_data), 2)  # Only location and is_available

    def test_profile_none_when_not_exists(self):
        """Test that profile is None when it doesn't exist."""
        user = User.objects.create_user(
            email="noprofile@example.com",
            username="noprofile",
            password="pass123",
        )

        serializer = UserListSerializer(user)
        self.assertIsNone(serializer.data["profile"])

    def test_all_fields_are_read_only(self):
        """Test that all fields are read-only."""
        serializer = UserListSerializer()
        for field_name in serializer.Meta.fields:
            field = serializer.fields[field_name]
            if field_name not in ["profile", "full_name", "profile_picture_url"]:
                self.assertTrue(field.read_only)
