"""
Integration tests for accounts app.

This module contains integration tests that verify the interaction between
different components of the accounts app, including end-to-end workflows.
"""

from accounts.tests.test_utils import TestDataFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationToLoginFlowTestCase(APITestCase):
    """Test complete user registration to login flow."""

    def test_complete_registration_and_login_flow(self):
        """Test user can register and then login."""
        # Step 1: Register a new user
        registration_data = TestDataFactory.get_valid_registration_data(
            email="newuser@example.com",
            username="newuser",
            include_profile=True,
        )

        register_url = reverse("accounts:register")
        register_response = self.client.post(
            register_url, registration_data, format="json"
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        user_id = register_response.data["id"]

        # Step 2: Activate the user (normally done by admin)
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        # Step 3: Login with the registered credentials
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"],
        }

        login_url = reverse("accounts:token_obtain_pair")
        login_response = self.client.post(login_url, login_data, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)
        self.assertIn("user", login_response.data)

        # Step 4: Verify user data in login response
        user_data = login_response.data["user"]
        self.assertEqual(user_data["email"], registration_data["email"])
        self.assertEqual(user_data["username"], registration_data["username"])

        # Step 5: Verify profile data in login response
        profile_data = user_data["profile"]
        self.assertEqual(profile_data["bio"], registration_data["profile"]["bio"])
        self.assertEqual(
            profile_data["location"], registration_data["profile"]["location"]
        )


class UserProfileManagementFlowTestCase(APITestCase):
    """Test complete user profile management flow."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)

    def test_complete_profile_management_flow(self):
        """Test user can view and update their profile."""
        # Step 1: Get current user profile
        current_user_url = reverse("accounts:current_user")
        get_response = self.client.get(current_user_url)

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        get_response.data["first_name"]

        # Step 2: Update profile
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "profile": {
                "bio": "Updated bio",
                "location": "New York",
                "is_available": False,
            },
        }

        update_url = reverse("accounts:profile_update")
        update_response = self.client.patch(update_url, update_data, format="json")

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Step 3: Verify changes by getting profile again
        verify_response = self.client.get(current_user_url)

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_response.data["first_name"], "Updated")
        self.assertEqual(verify_response.data["last_name"], "Name")
        self.assertEqual(verify_response.data["profile"]["bio"], "Updated bio")
        self.assertEqual(verify_response.data["profile"]["location"], "New York")
        self.assertFalse(verify_response.data["profile"]["is_available"])


class UserSearchAndDiscoveryFlowTestCase(APITestCase):
    """Test user search and discovery flow."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.client.force_authenticate(user=self.user)

        # Create multiple users for search testing
        self.user1 = TestDataFactory.create_user(
            email="john@example.com",
            username="john",
            first_name="John",
            last_name="Doe",
            is_active=True,
        )
        TestDataFactory.create_profile(
            self.user1, location="New York", is_available=True
        )

        self.user2 = TestDataFactory.create_user(
            email="jane@example.com",
            username="jane",
            first_name="Jane",
            last_name="Smith",
            is_active=True,
        )
        TestDataFactory.create_profile(
            self.user2, location="San Francisco", is_available=True
        )

    def test_search_and_view_user_flow(self):
        """Test searching for users and viewing their profiles."""
        # Step 1: Search for users by name
        list_url = reverse("accounts:user_list")
        search_response = self.client.get(list_url, {"search": "John"})

        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_response.data["results"]), 1)

        found_user_id = search_response.data["results"][0]["id"]
        self.assertEqual(found_user_id, self.user1.id)

        # Step 2: View detailed profile of found user
        detail_url = reverse("accounts:user_detail", kwargs={"pk": found_user_id})
        detail_response = self.client.get(detail_url)

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["first_name"], "John")
        self.assertEqual(detail_response.data["last_name"], "Doe")
        self.assertEqual(detail_response.data["profile"]["location"], "New York")

    def test_filter_users_by_location_and_availability(self):
        """Test filtering users by multiple criteria."""
        list_url = reverse("accounts:user_list")

        # Filter by location
        response = self.client.get(list_url, {"location": "New York"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_ids = [user["id"] for user in response.data["results"]]
        self.assertIn(self.user1.id, user_ids)
        self.assertNotIn(self.user2.id, user_ids)

        # Filter by availability
        response = self.client.get(list_url, {"is_available": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)


class TokenRefreshFlowTestCase(APITestCase):
    """Test JWT token refresh flow."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        TestDataFactory.create_profile(self.user)

    def test_token_refresh_flow(self):
        """Test obtaining and refreshing JWT tokens."""
        # Step 1: Login to get tokens
        login_url = reverse("accounts:token_obtain_pair")
        login_data = {
            "email": self.user.email,
            "password": "testpass123",
        }

        login_response = self.client.post(login_url, login_data, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["refresh"]
        original_access_token = login_response.data["access"]

        # Step 2: Refresh the access token
        refresh_url = reverse("accounts:token_refresh")
        refresh_data = {"refresh": refresh_token}

        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        new_access_token = refresh_response.data["access"]
        self.assertNotEqual(original_access_token, new_access_token)

        # Step 3: Verify new token works
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        current_user_url = reverse("accounts:current_user")
        verify_response = self.client.get(current_user_url)

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_response.data["id"], self.user.id)


class ProfilePictureUploadFlowTestCase(APITestCase):
    """Test profile picture upload and update flow."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)

    def test_upload_and_update_profile_picture(self):
        """Test uploading and updating profile picture."""
        # Step 1: Upload initial profile picture
        image1 = TestDataFactory.create_test_image(
            width=200, height=200, color="red", filename="profile1.jpg"
        )

        update_url = reverse("accounts:profile_update")
        data1 = {"profile": {"profile_picture": image1}}

        response1 = self.client.patch(update_url, data1, format="multipart")

        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.profile_picture)
        original_picture_name = self.profile.profile_picture.name

        # Step 2: Update with new profile picture
        image2 = TestDataFactory.create_test_image(
            width=300, height=300, color="blue", filename="profile2.jpg"
        )

        data2 = {"profile": {"profile_picture": image2}}
        response2 = self.client.patch(update_url, data2, format="multipart")

        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.profile_picture)
        self.assertNotEqual(self.profile.profile_picture.name, original_picture_name)

        # Step 3: Verify picture is accessible in user detail
        current_user_url = reverse("accounts:current_user")
        response3 = self.client.get(current_user_url)

        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response3.data["profile"]["profile_picture_url"])


class MultiUserInteractionTestCase(APITestCase):
    """Test interactions between multiple users."""

    def setUp(self):
        """Set up test data."""
        self.user1 = TestDataFactory.create_user(
            email="user1@example.com",
            username="user1",
            is_active=True,
        )
        TestDataFactory.create_profile(self.user1, location="New York")

        self.user2 = TestDataFactory.create_user(
            email="user2@example.com",
            username="user2",
            is_active=True,
        )
        TestDataFactory.create_profile(self.user2, location="San Francisco")

    def test_users_can_view_each_others_profiles(self):
        """Test that users can view each other's profiles."""
        # User1 views User2's profile
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("accounts:user_detail", kwargs={"pk": self.user2.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user2.id)

        # User2 views User1's profile
        self.client.force_authenticate(user=self.user2)
        detail_url = reverse("accounts:user_detail", kwargs={"pk": self.user1.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user1.id)

    def test_users_cannot_update_each_others_profiles(self):
        """Test that users cannot update each other's profiles."""
        # User1 tries to update their own profile (should work)
        self.client.force_authenticate(user=self.user1)
        update_url = reverse("accounts:profile_update")
        data = {"first_name": "Updated"}

        response = self.client.patch(update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only user1 was updated
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.first_name, "Updated")
        self.assertNotEqual(self.user2.first_name, "Updated")

    def test_users_appear_in_each_others_search_results(self):
        """Test that users can find each other through search."""
        self.client.force_authenticate(user=self.user1)
        list_url = reverse("accounts:user_list")

        # Search for user2
        response = self.client.get(list_url, {"search": "user2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_ids = [user["id"] for user in response.data["results"]]
        self.assertIn(self.user2.id, user_ids)


class ErrorRecoveryFlowTestCase(APITestCase):
    """Test error recovery scenarios."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.profile = TestDataFactory.create_profile(self.user)
        self.client.force_authenticate(user=self.user)

    def test_recover_from_invalid_profile_update(self):
        """Test that profile remains unchanged after invalid update."""
        original_first_name = self.user.first_name
        original_bio = self.profile.bio

        # Attempt invalid update
        update_url = reverse("accounts:profile_update")
        invalid_data = {"first_name": ""}  # Empty first name is invalid

        response = self.client.patch(update_url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify data unchanged
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, original_first_name)
        self.assertEqual(self.profile.bio, original_bio)

        # Attempt valid update after error
        valid_data = {"first_name": "Updated"}
        response = self.client.patch(update_url, valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_handle_concurrent_profile_updates(self):
        """Test handling of concurrent profile updates."""
        update_url = reverse("accounts:profile_update")

        # First update
        data1 = {"first_name": "First"}
        response1 = self.client.patch(update_url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second update (should overwrite first)
        data2 = {"first_name": "Second"}
        response2 = self.client.patch(update_url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Verify final state
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Second")


class PaginationFlowTestCase(APITestCase):
    """Test pagination in user list."""

    def setUp(self):
        """Set up test data."""
        self.user = TestDataFactory.create_user(is_active=True)
        self.client.force_authenticate(user=self.user)

        # Create multiple users for pagination testing
        for i in range(15):
            user = TestDataFactory.create_user(
                email=f"user{i}@example.com",
                username=f"user{i}",
                is_active=True,
            )
            TestDataFactory.create_profile(user)

    def test_paginated_user_list(self):
        """Test that user list is properly paginated."""
        list_url = reverse("accounts:user_list")

        # Get first page
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        # Verify pagination metadata
        self.assertGreater(response.data["count"], 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

        # Get next page
        if response.data["next"]:
            next_response = self.client.get(response.data["next"])
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)
            self.assertIsNotNone(next_response.data["previous"])
