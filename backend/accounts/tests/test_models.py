"""
Unit tests for accounts models.

This module contains comprehensive tests for User and Profile models,
covering model creation, validation, relationships, and edge cases.
"""

from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
        }

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.role, User.Role.USER)
        self.assertFalse(user.is_active)  # Default is False
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpass123",
        )

        # Note: is_active might be False by default in this project
        # Superuser should have staff and superuser permissions
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_email_unique_constraint(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=self.user_data["email"],
                username="differentuser",
                password="testpass123",
            )

    def test_user_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_user_required_fields(self):
        """Test that REQUIRED_FIELDS contains expected fields."""
        expected_fields = ["username", "first_name", "last_name"]
        self.assertEqual(User.REQUIRED_FIELDS, expected_fields)

    def test_user_str_representation(self):
        """Test the string representation of User."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_user_role_choices(self):
        """Test user role choices."""
        self.assertEqual(User.Role.ADMIN, "ADMIN")
        self.assertEqual(User.Role.USER, "USER")

    def test_user_default_role(self):
        """Test that default role is USER."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.role, User.Role.USER)

    def test_user_admin_role(self):
        """Test creating user with ADMIN role."""
        admin_data = self.user_data.copy()
        admin_data["email"] = "admin@example.com"
        admin_data["username"] = "adminuser"
        admin_data["role"] = User.Role.ADMIN

        user = User.objects.create_user(**admin_data)
        self.assertEqual(user.role, User.Role.ADMIN)

    def test_user_timestamps(self):
        """Test that timestamps are set correctly."""
        user = User.objects.create_user(**self.user_data)

        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertLessEqual(user.created_at, timezone.now())
        self.assertLessEqual(user.updated_at, timezone.now())

    def test_user_updated_at_changes_on_save(self):
        """Test that updated_at changes when user is saved."""
        user = User.objects.create_user(**self.user_data)
        original_updated_at = user.updated_at

        # Wait a moment and update
        user.first_name = "Updated"
        user.save()

        self.assertGreater(user.updated_at, original_updated_at)

    def test_user_ordering(self):
        """Test that users are ordered by created_at descending."""
        user1 = User.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="pass123",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="pass123",
        )

        users = User.objects.all()
        self.assertEqual(users[0], user2)
        self.assertEqual(users[1], user1)

    def test_user_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data)
        expected_name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.get_full_name(), expected_name)

    def test_user_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), self.user_data["first_name"])


class ProfileModelTestCase(TestCase):
    """Test cases for the Profile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.profile_data = {
            "bio": "Test bio",
            "phone_number": "+1234567890",
            "location": "New York, USA",
            "timezone": "America/New_York",
            "language_preference": "en",
            "is_available": True,
        }

    def test_create_profile_with_valid_data(self):
        """Test creating a profile with valid data."""
        profile = Profile.objects.create(user=self.user, **self.profile_data)

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, self.profile_data["bio"])
        self.assertEqual(profile.phone_number, self.profile_data["phone_number"])
        self.assertEqual(profile.location, self.profile_data["location"])
        self.assertEqual(profile.timezone, self.profile_data["timezone"])
        self.assertEqual(
            profile.language_preference, self.profile_data["language_preference"]
        )
        self.assertEqual(profile.is_available, self.profile_data["is_available"])

    def test_profile_one_to_one_relationship(self):
        """Test that profile has one-to-one relationship with user."""
        profile = Profile.objects.create(user=self.user)

        self.assertEqual(self.user.profile, profile)
        self.assertEqual(profile.user, self.user)

    def test_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted."""
        profile = Profile.objects.create(user=self.user)
        profile_id = profile.id

        self.user.delete()

        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=profile_id)

    def test_profile_default_values(self):
        """Test profile default values."""
        profile = Profile.objects.create(user=self.user)

        self.assertEqual(profile.bio, "")
        # profile_picture can be None or empty string depending on field configuration
        self.assertFalse(profile.profile_picture)
        self.assertEqual(profile.phone_number, "")
        self.assertEqual(profile.location, "")
        self.assertEqual(profile.timezone, "UTC")
        self.assertEqual(profile.language_preference, "en")
        self.assertTrue(profile.is_available)

    def test_profile_str_representation(self):
        """Test the string representation of Profile."""
        profile = Profile.objects.create(user=self.user)
        expected_str = f"{self.user.email}'s profile"
        self.assertEqual(str(profile), expected_str)

    def test_profile_timestamps(self):
        """Test that profile timestamps are set correctly."""
        profile = Profile.objects.create(user=self.user)

        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        self.assertLessEqual(profile.created_at, timezone.now())
        self.assertLessEqual(profile.updated_at, timezone.now())

    def test_profile_updated_at_changes_on_save(self):
        """Test that updated_at changes when profile is saved."""
        profile = Profile.objects.create(user=self.user)
        original_updated_at = profile.updated_at

        profile.bio = "Updated bio"
        profile.save()

        self.assertGreater(profile.updated_at, original_updated_at)

    def test_profile_ordering(self):
        """Test that profiles are ordered by created_at descending."""
        user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="pass123",
        )

        profile1 = Profile.objects.create(user=self.user)
        profile2 = Profile.objects.create(user=user2)

        profiles = Profile.objects.all()
        self.assertEqual(profiles[0], profile2)
        self.assertEqual(profiles[1], profile1)

    def test_profile_bio_max_length(self):
        """Test that bio field accepts text up to max_length."""
        # Bio is a TextField with max_length=500
        # Test that it accepts exactly 500 characters
        bio_500 = "x" * 500
        profile = Profile.objects.create(user=self.user, bio=bio_500)
        self.assertEqual(len(profile.bio), 500)

        # Test that it can be validated with full_clean
        profile.full_clean()  # Should not raise

    def test_profile_phone_number_max_length(self):
        """Test that phone_number respects max_length constraint."""
        long_phone = "1" * 16  # Exceeds max_length of 15
        profile = Profile(user=self.user, phone_number=long_phone)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_location_max_length(self):
        """Test that location respects max_length constraint."""
        long_location = "x" * 101  # Exceeds max_length of 100
        profile = Profile(user=self.user, location=long_location)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_timezone_max_length(self):
        """Test that timezone respects max_length constraint."""
        long_timezone = "x" * 51  # Exceeds max_length of 50
        profile = Profile(user=self.user, timezone=long_timezone)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_language_preference_max_length(self):
        """Test that language_preference respects max_length constraint."""
        long_language = "x" * 11  # Exceeds max_length of 10
        profile = Profile(user=self.user, language_preference=long_language)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_profile_is_available_boolean(self):
        """Test that is_available is a boolean field."""
        profile = Profile.objects.create(user=self.user, is_available=False)
        self.assertFalse(profile.is_available)

        profile.is_available = True
        profile.save()
        self.assertTrue(profile.is_available)

    def test_profile_related_name(self):
        """Test that profile can be accessed via user.profile."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(self.user.profile, profile)
