"""
Unit tests for skillhub views.

This module contains comprehensive tests for all API views in the skillhub app,
covering authentication, permissions, CRUD operations, and custom actions.
"""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from skillhub.models import SkillCategory
from skillhub.models import SkillExchange
from skillhub.models import SkillFeedback
from skillhub.models import UserSkill
from skillhub.tests.test_utils import SkillHubTestDataFactory


class SkillCategoryViewSetTestCase(APITestCase):
    """Test cases for SkillCategoryViewSet."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = SkillHubTestDataFactory.create_user(
            email="admin@example.com",
            username="admin",
            is_staff=True,
        )
        self.regular_user = SkillHubTestDataFactory.create_user(
            email="user@example.com",
            username="user",
        )
        self.category = SkillHubTestDataFactory.create_category()
        self.list_url = reverse("skillhub:category-list")

    def test_list_categories_unauthenticated(self):
        """Test listing categories without authentication."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_authenticated(self):
        """Test listing categories with authentication."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_category(self):
        """Test retrieving a single category."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("skillhub:category-detail", kwargs={"pk": self.category.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

    def test_create_category_as_admin(self):
        """Test creating category as admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Web Development",
            "description": "Web development skills",
            "icon": "fa-globe",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SkillCategory.objects.count(), 2)

    def test_create_category_as_regular_user(self):
        """Test creating category as regular user."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "name": "Web Development",
            "description": "Web development skills",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_category_as_admin(self):
        """Test updating category as admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("skillhub:category-detail", kwargs={"pk": self.category.pk})
        data = {"name": "Updated Programming"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Programming")

    def test_delete_category_as_admin(self):
        """Test deleting category as admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("skillhub:category-detail", kwargs={"pk": self.category.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_toggle_category_status(self):
        """Test toggling category status."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(
            "skillhub:category-toggle-status", kwargs={"pk": self.category.pk}
        )

        original_status = self.category.is_active
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertNotEqual(self.category.is_active, original_status)

    def test_filter_categories_by_name(self):
        """Test filtering categories by name."""
        SkillHubTestDataFactory.create_category(name="Music")
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url, {"name": "Music"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_categories(self):
        """Test searching categories."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url, {"search": "Programming"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SkillViewSetTestCase(APITestCase):
    """Test cases for SkillViewSet."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = SkillHubTestDataFactory.create_user(
            email="admin@example.com",
            username="admin",
            is_staff=True,
        )
        self.regular_user = SkillHubTestDataFactory.create_user(
            email="user@example.com",
            username="user",
        )
        self.category = SkillHubTestDataFactory.create_category()
        self.skill = SkillHubTestDataFactory.create_skill(category=self.category)
        self.list_url = reverse("skillhub:skill-list")

    def test_list_skills_unauthenticated(self):
        """Test listing skills without authentication."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_skills_authenticated(self):
        """Test listing skills with authentication."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_skill(self):
        """Test retrieving a single skill."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("skillhub:skill-detail", kwargs={"pk": self.skill.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.skill.name)

    def test_create_skill_as_admin(self):
        """Test creating skill as admin."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "JavaScript Programming",
            "category": self.category.id,
            "description": "Learn JavaScript from basics to advanced concepts. " * 5,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_skill_as_regular_user(self):
        """Test creating skill as regular user fails."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "name": "JavaScript Programming",
            "category": self.category.id,
            "description": "Learn JavaScript, useful for React, Angular, and Vue. ",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_skill_as_admin(self):
        """Test updating skill as admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("skillhub:skill-detail", kwargs={"pk": self.skill.pk})
        data = {"name": "Updated Python Programming"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_skill_as_admin(self):
        """Test deleting skill as admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("skillhub:skill-detail", kwargs={"pk": self.skill.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_toggle_skill_status(self):
        """Test toggling skill status."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("skillhub:skill-toggle-status", kwargs={"pk": self.skill.pk})

        original_status = self.skill.is_active
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertNotEqual(self.skill.is_active, original_status)

    def test_filter_skills_by_category(self):
        """Test filtering skills by category."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url, {"category": self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_skills(self):
        """Test searching skills."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url, {"search": "Python"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_skills_by_category_action(self):
        """Test getting skills by category custom action."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse(
            "skillhub:skill-by-category", kwargs={"category_id": self.category.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserSkillViewSetTestCase(APITestCase):
    """Test cases for UserSkillViewSet."""

    def setUp(self):
        """Set up test data."""
        self.user = SkillHubTestDataFactory.create_user()
        self.other_user = SkillHubTestDataFactory.create_user(
            email="other@example.com",
            username="other",
        )
        self.skill = SkillHubTestDataFactory.create_skill()
        self.user_skill = SkillHubTestDataFactory.create_user_skill(
            user=self.user,
            skill=self.skill,
        )
        self.list_url = reverse("skillhub:teaching-skill-list")

    def test_list_user_skills_unauthenticated(self):
        """Test listing user skills without authentication."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_skills_authenticated(self):
        """Test listing user skills with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_user_skill(self):
        """Test retrieving a single user skill."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "skillhub:teaching-skill-detail", kwargs={"pk": self.user_skill.pk}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["skill"], self.skill.id)

    def test_create_user_skill(self):
        """Test creating a user skill."""
        self.client.force_authenticate(user=self.user)
        skill2 = SkillHubTestDataFactory.create_skill(name="Java Programming")

        data = {
            "skill": skill2.id,
            "proficiency_level": UserSkill.ProficiencyLevel.INTERMEDIATE,
            "years_of_experience": 3,
            "learning_outcomes": "Master Java programming",
            "teaching_methods": "Hands-on projects and exercises",
            "estimated_duration": 40,
            "duration_type": UserSkill.DurationType.HOURS,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserSkill.objects.filter(user=self.user).count(), 2)

    def test_update_own_user_skill(self):
        """Test updating own user skill."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "skillhub:teaching-skill-detail", kwargs={"pk": self.user_skill.pk}
        )
        data = {"years_of_experience": 5}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_skill.refresh_from_db()
        self.assertEqual(self.user_skill.years_of_experience, 5)

    def test_update_other_user_skill_fails(self):
        """Test updating another user's skill fails."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse(
            "skillhub:teaching-skill-detail", kwargs={"pk": self.user_skill.pk}
        )
        data = {"years_of_experience": 5}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_user_skill(self):
        """Test deleting own user skill."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "skillhub:teaching-skill-detail", kwargs={"pk": self.user_skill.pk}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_toggle_availability(self):
        """Test toggling user skill availability."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "skillhub:teaching-skill-toggle-availability",
            kwargs={"pk": self.user_skill.pk},
        )

        original_status = self.user_skill.is_active
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_skill.refresh_from_db()
        self.assertNotEqual(self.user_skill.is_active, original_status)

    def test_add_milestone(self):
        """Test adding milestone to user skill."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "skillhub:teaching-skill-add-milestone", kwargs={"pk": self.user_skill.pk}
        )

        data = {
            "title": "Learn Basics",
            "description": "Master the fundamentals",
            "order": 1,
            "estimated_hours": 10,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user_skill.milestones.count(), 1)

    def test_update_milestone(self):
        """Test updating a milestone."""
        self.client.force_authenticate(user=self.user)
        milestone = SkillHubTestDataFactory.create_milestone(user_skill=self.user_skill)

        url = reverse(
            "skillhub:teaching-skill-update-milestone",
            kwargs={"pk": self.user_skill.pk, "milestone_id": milestone.id},
        )
        data = {"title": "Updated Title"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        milestone.refresh_from_db()
        self.assertEqual(milestone.title, "Updated Title")

    def test_delete_milestone(self):
        """Test deleting a milestone."""
        self.client.force_authenticate(user=self.user)
        milestone = SkillHubTestDataFactory.create_milestone(user_skill=self.user_skill)

        url = reverse(
            "skillhub:teaching-skill-delete-milestone",
            kwargs={"pk": self.user_skill.pk, "milestone_id": milestone.id},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user_skill.milestones.count(), 0)

    def test_reorder_milestones(self):
        """Test reordering milestones."""
        self.client.force_authenticate(user=self.user)
        milestone1 = SkillHubTestDataFactory.create_milestone(
            user_skill=self.user_skill,
            order=1,
        )
        milestone2 = SkillHubTestDataFactory.create_milestone(
            user_skill=self.user_skill,
            order=2,
            title="Milestone 2",
        )

        url = reverse(
            "skillhub:teaching-skill-reorder-milestones",
            kwargs={"pk": self.user_skill.pk},
        )
        data = {
            "orders": [
                {"id": milestone1.id, "order": 2},
                {"id": milestone2.id, "order": 1},
            ]
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_user_skills_by_skill(self):
        """Test filtering user skills by skill."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"skill": self.skill.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_user_skills(self):
        """Test searching user skills."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"search": "Python"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SkillExchangeViewSetTestCase(APITestCase):
    """Test cases for SkillExchangeViewSet."""

    def setUp(self):
        """Set up test data."""
        self.teacher = SkillHubTestDataFactory.create_user(
            email="teacher@example.com",
            username="teacher",
        )
        self.learner = SkillHubTestDataFactory.create_user(
            email="learner@example.com",
            username="learner",
        )
        self.user_skill = SkillHubTestDataFactory.create_user_skill(user=self.teacher)
        self.exchange = SkillHubTestDataFactory.create_exchange(
            user_skill=self.user_skill,
            learner=self.learner,
        )
        self.list_url = reverse("skillhub:exchange-list")

    def test_list_exchanges_unauthenticated(self):
        """Test listing exchanges without authentication."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_exchanges_as_teacher(self):
        """Test listing exchanges as teacher."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_list_exchanges_as_learner(self):
        """Test listing exchanges as learner."""
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_retrieve_exchange(self):
        """Test retrieving a single exchange."""
        self.client.force_authenticate(user=self.learner)
        url = reverse("skillhub:exchange-detail", kwargs={"pk": self.exchange.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_exchange_request(self):
        """Test creating an exchange request."""
        self.client.force_authenticate(user=self.learner)
        teacher2 = SkillHubTestDataFactory.create_user(
            email="teacher2@example.com",
            username="teacher2",
        )
        user_skill2 = SkillHubTestDataFactory.create_user_skill(user=teacher2)

        data = {
            "user_skill": user_skill2.id,
            "learning_goals": "Learn advanced programming concepts",
            "availability": "Weekdays 6-8 PM, Weekends anytime",
            "proposed_duration": 30,
            "notes": "Looking forward to learning",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accept_exchange_as_teacher(self):
        """Test accepting exchange as teacher."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {"status": SkillExchange.Status.ACCEPTED}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, SkillExchange.Status.ACCEPTED)

    def test_accept_exchange_as_learner_fails(self):
        """Test accepting exchange as learner fails."""
        self.client.force_authenticate(user=self.learner)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {"status": SkillExchange.Status.ACCEPTED}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_exchange_with_reason(self):
        """Test cancelling exchange with reason."""
        self.client.force_authenticate(user=self.learner)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {
            "status": SkillExchange.Status.CANCELLED,
            "reason": "I need to cancel due to time constraints and other commitments.",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, SkillExchange.Status.CANCELLED)

    def test_cancel_exchange_without_reason_fails(self):
        """Test cancelling exchange without reason fails."""
        self.client.force_authenticate(user=self.learner)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {"status": SkillExchange.Status.CANCELLED}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_exchange(self):
        """Test starting an exchange."""
        self.exchange.status = SkillExchange.Status.ACCEPTED
        self.exchange.save()

        self.client.force_authenticate(user=self.teacher)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {"status": SkillExchange.Status.IN_PROGRESS}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_exchange(self):
        """Test completing an exchange."""
        self.exchange.status = SkillExchange.Status.IN_PROGRESS
        self.exchange.save()

        self.client.force_authenticate(user=self.teacher)
        url = reverse(
            "skillhub:exchange-update-status", kwargs={"pk": self.exchange.pk}
        )

        data = {"status": SkillExchange.Status.COMPLETED}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_exchanges_by_status(self):
        """Test filtering exchanges by status."""
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(
            self.list_url, {"status": SkillExchange.Status.PENDING}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_exchanges(self):
        """Test searching exchanges."""
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(self.list_url, {"search": "Python"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SkillFeedbackViewSetTestCase(APITestCase):
    """Test cases for SkillFeedbackViewSet."""

    def setUp(self):
        """Set up test data."""
        self.teacher = SkillHubTestDataFactory.create_user(
            email="teacher@example.com",
            username="teacher",
        )
        self.learner = SkillHubTestDataFactory.create_user(
            email="learner@example.com",
            username="learner",
        )
        self.user_skill = SkillHubTestDataFactory.create_user_skill(user=self.teacher)
        self.exchange = SkillHubTestDataFactory.create_exchange(
            user_skill=self.user_skill,
            learner=self.learner,
            status=SkillExchange.Status.COMPLETED,
        )
        self.list_url = reverse("skillhub:feedback-list")

    def test_list_feedback_unauthenticated(self):
        """Test listing feedback without authentication."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_feedback_authenticated(self):
        """Test listing feedback with authentication."""
        self.client.force_authenticate(user=self.learner)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_feedback(self):
        """Test creating feedback for completed exchange."""
        self.client.force_authenticate(user=self.learner)

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Excellent teacher! Very patient and knowledgeable. Highly recommended.",
            "is_recommended": True,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SkillFeedback.objects.count(), 1)

    def test_create_feedback_for_non_completed_exchange_fails(self):
        """Test creating feedback for non-completed exchange fails."""
        self.client.force_authenticate(user=self.learner)
        pending_exchange = SkillHubTestDataFactory.create_exchange(
            user_skill=self.user_skill,
            learner=self.learner,
            status=SkillExchange.Status.PENDING,
        )

        data = {
            "exchange": pending_exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Great teacher!",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_feedback(self):
        """Test retrieving feedback."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        self.client.force_authenticate(user=self.learner)
        url = reverse("skillhub:feedback-detail", kwargs={"pk": feedback.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_feedback_within_window(self):
        """Test updating feedback within update window."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        self.client.force_authenticate(user=self.learner)
        url = reverse("skillhub:feedback-detail", kwargs={"pk": feedback.pk})

        data = {
            "rating": Decimal("5.0"),
            "comment": "Updated: Absolutely excellent teacher! Best experience ever.",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_user_feedback_fails(self):
        """Test updating another user's feedback fails."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        other_user = SkillHubTestDataFactory.create_user(
            email="other@example.com",
            username="other",
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("skillhub:feedback-detail", kwargs={"pk": feedback.pk})

        data = {"rating": Decimal("1.0")}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_feedback_not_allowed(self):
        """Test deleting feedback is not allowed."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        self.client.force_authenticate(user=self.learner)
        url = reverse("skillhub:feedback-detail", kwargs={"pk": feedback.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_feedback_stats(self):
        """Test getting feedback statistics."""
        SkillHubTestDataFactory.create_feedback(
            exchange=self.exchange,
            rating=Decimal("4.5"),
        )

        self.client.force_authenticate(user=self.teacher)
        url = reverse(
            "skillhub:feedback-get-stats", kwargs={"user_skill_id": self.user_skill.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_reviews", response.data)
        self.assertIn("average_rating", response.data)

    def test_get_eligible_exchanges(self):
        """Test getting eligible exchanges for feedback."""
        self.client.force_authenticate(user=self.learner)
        url = reverse("skillhub:feedback-eligible-exchanges")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_search_feedback(self):
        """Test searching feedback."""
        SkillHubTestDataFactory.create_feedback(
            exchange=self.exchange,
            comment="Great teacher! Very helpful and patient.",
        )

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.list_url, {"search": "helpful"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_feedback_by_rating(self):
        """Test filtering feedback by rating."""
        SkillHubTestDataFactory.create_feedback(
            exchange=self.exchange,
            rating=Decimal("5.0"),
        )

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.list_url, {"rating": "5.0"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ViewSetPaginationTestCase(APITestCase):
    """Test cases for pagination across viewsets."""

    def setUp(self):
        """Set up test data."""
        self.user = SkillHubTestDataFactory.create_user()
        self.client.force_authenticate(user=self.user)

    def test_category_list_pagination(self):
        """Test category list pagination."""
        # Create multiple categories
        for i in range(15):
            SkillHubTestDataFactory.create_category(name=f"Category {i}")

        url = reverse("skillhub:category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("results", response.data)

    def test_skill_list_pagination(self):
        """Test skill list pagination."""
        category = SkillHubTestDataFactory.create_category()
        for i in range(15):
            SkillHubTestDataFactory.create_skill(
                name=f"Skill {i}",
                category=category,
            )

        url = reverse("skillhub:skill-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)


class ViewSetOrderingTestCase(APITestCase):
    """Test cases for ordering across viewsets."""

    def setUp(self):
        """Set up test data."""
        self.user = SkillHubTestDataFactory.create_user()
        self.client.force_authenticate(user=self.user)

    def test_category_ordering_by_name(self):
        """Test ordering categories by name."""
        SkillHubTestDataFactory.create_category(name="Zebra")
        SkillHubTestDataFactory.create_category(name="Alpha")

        url = reverse("skillhub:category-list")
        response = self.client.get(url, {"ordering": "name"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["name"], "Alpha")

    def test_skill_ordering_by_created_at(self):
        """Test ordering skills by created_at."""
        category = SkillHubTestDataFactory.create_category()
        SkillHubTestDataFactory.create_skill(name="Skill 1", category=category)
        SkillHubTestDataFactory.create_skill(name="Skill 2", category=category)

        url = reverse("skillhub:skill-list")
        response = self.client.get(url, {"ordering": "-created_at"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
