"""
Unit tests for skillhub serializers.

This module contains comprehensive tests for all serializers in the skillhub app,
covering validation, serialization, deserialization, and edge cases.
"""

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from skillhub.models import SkillCategory
from skillhub.models import SkillExchange
from skillhub.models import UserSkill
from skillhub.serializers import SkillCategorySerializer
from skillhub.serializers import SkillDetailSerializer
from skillhub.serializers import SkillExchangeDetailSerializer
from skillhub.serializers import SkillExchangeListSerializer
from skillhub.serializers import SkillExchangeStatusUpdateSerializer
from skillhub.serializers import SkillFeedbackCreateSerializer
from skillhub.serializers import SkillFeedbackDetailSerializer
from skillhub.serializers import SkillFeedbackListSerializer
from skillhub.serializers import SkillFeedbackUpdateSerializer
from skillhub.serializers import SkillListSerializer
from skillhub.serializers import SkillMilestoneSerializer
from skillhub.serializers import UserSkillDetailSerializer
from skillhub.serializers import UserSkillListSerializer
from skillhub.tests.test_utils import SkillHubTestDataFactory


class SkillCategorySerializerTestCase(TestCase):
    """Test cases for SkillCategorySerializer."""

    def setUp(self):
        """Set up test data."""
        self.category = SkillHubTestDataFactory.create_category()
        self.valid_data = {
            "name": "Web Development",
            "description": "Web development skills",
            "icon": "fa-globe",
        }

    def test_serialize_category(self):
        """Test serializing a category."""
        serializer = SkillCategorySerializer(self.category)
        data = serializer.data

        self.assertEqual(data["name"], self.category.name)
        self.assertEqual(data["description"], self.category.description)
        self.assertIn("skills_count", data)

    def test_deserialize_valid_category(self):
        """Test deserializing valid category data."""
        serializer = SkillCategorySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()

        self.assertEqual(category.name, self.valid_data["name"])
        self.assertEqual(category.description, self.valid_data["description"])

    def test_validate_name_too_short(self):
        """Test validation fails for name too short."""
        data = self.valid_data.copy()
        data["name"] = "AB"

        serializer = SkillCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_name_too_long(self):
        """Test validation fails for name too long."""
        data = self.valid_data.copy()
        data["name"] = "x" * 101

        serializer = SkillCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_name_special_characters(self):
        """Test validation fails for invalid special characters."""
        data = self.valid_data.copy()
        data["name"] = "Test@Category!"

        serializer = SkillCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_name_case_insensitive_uniqueness(self):
        """Test case-insensitive uniqueness validation."""
        SkillCategory.objects.create(name="Unique Category Name")

        data = self.valid_data.copy()
        data["name"] = "UNIQUE CATEGORY NAME"

        serializer = SkillCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_icon_invalid_characters(self):
        """Test validation fails for invalid icon characters."""
        data = self.valid_data.copy()
        data["icon"] = "fa-code@#$"

        serializer = SkillCategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("icon", serializer.errors)


class SkillSerializerTestCase(TestCase):
    """Test cases for Skill serializers."""

    def setUp(self):
        """Set up test data."""
        self.category = SkillHubTestDataFactory.create_category()
        self.skill = SkillHubTestDataFactory.create_skill(category=self.category)
        self.valid_data = {
            "name": "JavaScript Programming",
            "category": self.category.id,
            "description": "Learn JavaScript from basics to advanced. " * 5,
        }

    def test_serialize_skill_list(self):
        """Test serializing skill for list view."""
        serializer = SkillListSerializer(self.skill)
        data = serializer.data

        self.assertEqual(data["name"], self.skill.name)
        self.assertIn("category_name", data)

    def test_serialize_skill_detail(self):
        """Test serializing skill for detail view."""
        serializer = SkillDetailSerializer(self.skill)
        data = serializer.data

        self.assertEqual(data["name"], self.skill.name)
        self.assertIn("category_details", data)

    def test_deserialize_valid_skill(self):
        """Test deserializing valid skill data."""
        serializer = SkillDetailSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        skill = serializer.save()

        self.assertEqual(skill.name, self.valid_data["name"])
        self.assertEqual(skill.category.id, self.valid_data["category"])

    def test_validate_name_too_short(self):
        """Test validation fails for name too short."""
        data = self.valid_data.copy()
        data["name"] = "AB"

        serializer = SkillDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_description_too_short(self):
        """Test validation fails for description too short."""
        data = self.valid_data.copy()
        data["description"] = "Short"

        serializer = SkillDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_validate_description_too_many_urls(self):
        """Test validation fails for too many URLs in description."""
        data = self.valid_data.copy()
        data["description"] = (
            "Check http://1.com http://2.com http://3.com http://4.com http://5.com http://6.com"
        )

        serializer = SkillDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_validate_inactive_category(self):
        """Test validation fails for inactive category."""
        inactive_category = SkillCategory.objects.create(
            name="Inactive",
            is_active=False,
        )

        data = self.valid_data.copy()
        data["category"] = inactive_category.id

        serializer = SkillDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("category", serializer.errors)


class UserSkillSerializerTestCase(TestCase):
    """Test cases for UserSkill serializers."""

    def setUp(self):
        """Set up test data."""
        self.user = SkillHubTestDataFactory.create_user()
        self.skill = SkillHubTestDataFactory.create_skill()
        self.user_skill = SkillHubTestDataFactory.create_user_skill(
            user=self.user,
            skill=self.skill,
        )
        self.factory = APIRequestFactory()

    def test_serialize_user_skill_list(self):
        """Test serializing user skill for list view."""
        serializer = UserSkillListSerializer(self.user_skill)
        data = serializer.data

        self.assertEqual(data["skill"], self.user_skill.skill.id)
        self.assertIn("skill_name", data)
        self.assertIn("rating", data)

    def test_serialize_user_skill_detail(self):
        """Test serializing user skill for detail view."""
        serializer = UserSkillDetailSerializer(self.user_skill)
        data = serializer.data

        self.assertEqual(data["skill"], self.user_skill.skill.id)
        self.assertIn("skill_details", data)
        self.assertIn("milestones", data)

    def test_create_user_skill(self):
        """Test creating user skill via serializer."""
        request = self.factory.post("/")
        request.user = self.user

        skill2 = SkillHubTestDataFactory.create_skill(name="Java")
        data = {
            "skill": skill2.id,
            "proficiency_level": UserSkill.ProficiencyLevel.ADVANCED,
            "years_of_experience": 5,
            "learning_outcomes": "Master Java programming",
            "teaching_methods": "Hands-on projects",
            "estimated_duration": 60,
            "duration_type": UserSkill.DurationType.HOURS,
        }

        serializer = UserSkillDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())
        user_skill = serializer.save()

        self.assertEqual(user_skill.user, self.user)
        self.assertEqual(user_skill.skill, skill2)

    def test_validate_inactive_skill(self):
        """Test validation fails for inactive skill."""
        request = self.factory.post("/")
        request.user = self.user

        inactive_skill = SkillHubTestDataFactory.create_skill(
            name="Inactive Skill",
            is_active=False,
        )

        data = {
            "skill": inactive_skill.id,
            "proficiency_level": UserSkill.ProficiencyLevel.INTERMEDIATE,
            "years_of_experience": 3,
            "learning_outcomes": "Learn skill",
            "teaching_methods": "Online",
            "estimated_duration": 40,
        }

        serializer = UserSkillDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("skill", serializer.errors)

    def test_validate_duplicate_user_skill(self):
        """Test validation fails for duplicate user skill."""
        request = self.factory.post("/")
        request.user = self.user

        data = {
            "skill": self.skill.id,
            "proficiency_level": UserSkill.ProficiencyLevel.INTERMEDIATE,
            "years_of_experience": 3,
            "learning_outcomes": "Learn skill",
            "teaching_methods": "Online",
            "estimated_duration": 40,
        }

        serializer = UserSkillDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("skill", serializer.errors)

    def test_validate_duration_exceeds_maximum(self):
        """Test validation fails when duration exceeds maximum."""
        request = self.factory.post("/")
        request.user = self.user

        skill2 = SkillHubTestDataFactory.create_skill(name="Test Skill")
        data = {
            "skill": skill2.id,
            "proficiency_level": UserSkill.ProficiencyLevel.INTERMEDIATE,
            "years_of_experience": 3,
            "learning_outcomes": "Learn skill",
            "teaching_methods": "Online",
            "estimated_duration": 100,
            "duration_type": UserSkill.DurationType.HOURS,
        }

        serializer = UserSkillDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("estimated_duration", serializer.errors)


class SkillMilestoneSerializerTestCase(TestCase):
    """Test cases for SkillMilestoneSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user_skill = SkillHubTestDataFactory.create_user_skill()

    def test_serialize_milestone(self):
        """Test serializing a milestone."""
        milestone = SkillHubTestDataFactory.create_milestone(user_skill=self.user_skill)
        serializer = SkillMilestoneSerializer(milestone)
        data = serializer.data

        self.assertEqual(data["title"], milestone.title)
        self.assertEqual(data["order"], milestone.order)

    def test_create_milestone(self):
        """Test creating a milestone via serializer."""
        data = {
            "title": "Learn Advanced Concepts",
            "description": "Master advanced programming concepts",
            "order": 2,
            "estimated_hours": 20,
        }

        serializer = SkillMilestoneSerializer(
            data=data,
            context={"user_skill": self.user_skill},
        )
        self.assertTrue(serializer.is_valid())
        milestone = serializer.save(user_skill=self.user_skill)

        self.assertEqual(milestone.title, data["title"])
        self.assertEqual(milestone.user_skill, self.user_skill)


class SkillExchangeSerializerTestCase(TestCase):
    """Test cases for SkillExchange serializers."""

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
        self.factory = APIRequestFactory()

    def test_serialize_exchange_list(self):
        """Test serializing exchange for list view."""
        serializer = SkillExchangeListSerializer(self.exchange)
        data = serializer.data

        self.assertEqual(data["user_skill"], self.user_skill.id)
        self.assertIn("teacher_skill", data)
        self.assertIn("status_display", data)

    def test_serialize_exchange_detail(self):
        """Test serializing exchange for detail view."""
        serializer = SkillExchangeDetailSerializer(self.exchange)
        data = serializer.data

        self.assertEqual(data["user_skill"], self.user_skill.id)
        self.assertIn("teacher_skill", data)
        self.assertIn("learning_goals", data)

    def test_create_exchange(self):
        """Test creating exchange via serializer."""
        request = self.factory.post("/")
        request.user = self.learner

        teacher2 = SkillHubTestDataFactory.create_user(
            email="teacher2@example.com",
            username="teacher2",
        )
        user_skill2 = SkillHubTestDataFactory.create_user_skill(user=teacher2)

        data = {
            "user_skill": user_skill2.id,
            "learning_goals": "Learn advanced concepts",
            "availability": "Weekdays 6-8 PM",
            "proposed_duration": 30,
            "notes": "Looking forward to learning",
        }

        serializer = SkillExchangeDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())
        exchange = serializer.save()

        self.assertEqual(exchange.learner, self.learner)
        self.assertEqual(exchange.user_skill, user_skill2)
        self.assertEqual(exchange.status, SkillExchange.Status.PENDING)

    def test_validate_own_skill(self):
        """Test validation fails when requesting own skill."""
        request = self.factory.post("/")
        request.user = self.teacher

        data = {
            "user_skill": self.user_skill.id,
            "learning_goals": "Learn my own skill",
            "availability": "Anytime",
            "proposed_duration": 20,
        }

        serializer = SkillExchangeDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("user_skill", serializer.errors)

    def test_validate_inactive_skill(self):
        """Test validation fails for inactive skill."""
        request = self.factory.post("/")
        request.user = self.learner

        inactive_user_skill = SkillHubTestDataFactory.create_user_skill(is_active=False)

        data = {
            "user_skill": inactive_user_skill.id,
            "learning_goals": "Learn skill",
            "availability": "Anytime",
            "proposed_duration": 20,
        }

        serializer = SkillExchangeDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("user_skill", serializer.errors)

    def test_validate_duplicate_active_request(self):
        """Test validation fails for duplicate active request."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "user_skill": self.user_skill.id,
            "learning_goals": "Learn skill",
            "availability": "Weekends",
            "proposed_duration": 20,
        }

        serializer = SkillExchangeDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())

    def test_validate_availability_too_short(self):
        """Test validation fails for too short availability."""
        request = self.factory.post("/")
        request.user = self.learner

        teacher2 = SkillHubTestDataFactory.create_user(
            email="teacher2@example.com",
            username="teacher2",
        )
        user_skill2 = SkillHubTestDataFactory.create_user_skill(user=teacher2)

        data = {
            "user_skill": user_skill2.id,
            "learning_goals": "Learn skill",
            "availability": "Short",
            "proposed_duration": 20,
        }

        serializer = SkillExchangeDetailSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("availability", serializer.errors)


class SkillExchangeStatusUpdateSerializerTestCase(TestCase):
    """Test cases for SkillExchangeStatusUpdateSerializer."""

    def test_valid_status_update(self):
        """Test valid status update."""
        data = {
            "status": SkillExchange.Status.ACCEPTED,
        }

        serializer = SkillExchangeStatusUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_cancelled_status_requires_reason(self):
        """Test that CANCELLED status requires reason."""
        data = {
            "status": SkillExchange.Status.CANCELLED,
        }

        serializer = SkillExchangeStatusUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("reason", serializer.errors)

    def test_cancelled_status_with_short_reason(self):
        """Test that CANCELLED status requires detailed reason."""
        data = {
            "status": SkillExchange.Status.CANCELLED,
            "reason": "Short",
        }

        serializer = SkillExchangeStatusUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("reason", serializer.errors)

    def test_cancelled_status_with_valid_reason(self):
        """Test CANCELLED status with valid reason."""
        data = {
            "status": SkillExchange.Status.CANCELLED,
            "reason": "I need to cancel due to time constraints and other commitments.",
        }

        serializer = SkillExchangeStatusUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class SkillFeedbackSerializerTestCase(TestCase):
    """Test cases for SkillFeedback serializers."""

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
        self.factory = APIRequestFactory()

    def test_serialize_feedback_list(self):
        """Test serializing feedback for list view."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)
        serializer = SkillFeedbackListSerializer(feedback)
        data = serializer.data

        self.assertIn("teacher_name", data)
        self.assertIn("student_name", data)
        self.assertIn("rating", data)

    def test_serialize_feedback_detail(self):
        """Test serializing feedback for detail view."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)
        serializer = SkillFeedbackDetailSerializer(feedback)
        data = serializer.data

        self.assertIn("exchange_details", data)
        self.assertIn("is_within_update_window", data)

    def test_create_feedback(self):
        """Test creating feedback via serializer."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Excellent teacher! Very patient and knowledgeable.",
            "is_recommended": True,
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid())
        feedback = serializer.save()

        self.assertEqual(feedback.exchange, self.exchange)
        self.assertEqual(feedback.rating, Decimal("4.5"))

    def test_validate_rating_out_of_range(self):
        """Test validation fails for rating out of range."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("6.0"),
            "comment": "Great teacher!",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_validate_rating_invalid_increment(self):
        """Test validation fails for invalid rating increment."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.3"),
            "comment": "Great teacher!",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_validate_comment_too_short(self):
        """Test validation fails for comment too short."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Good",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("comment", serializer.errors)

    def test_validate_comment_too_many_urls(self):
        """Test validation fails for too many URLs in comment."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Check http://1.com http://2.com http://3.com for more info",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("comment", serializer.errors)

    def test_validate_comment_with_html(self):
        """Test validation fails for HTML in comment."""
        request = self.factory.post("/")
        request.user = self.learner

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "<script>alert('test')</script> Great teacher!",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("comment", serializer.errors)

    def test_validate_exchange_not_completed(self):
        """Test validation fails for non-completed exchange."""
        request = self.factory.post("/")
        request.user = self.learner

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

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("exchange", serializer.errors)

    def test_validate_duplicate_feedback(self):
        """Test validation fails for duplicate feedback."""
        request = self.factory.post("/")
        request.user = self.learner

        # Create existing feedback
        SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        data = {
            "exchange": self.exchange.id,
            "rating": Decimal("4.5"),
            "comment": "Another feedback",
        }

        serializer = SkillFeedbackCreateSerializer(
            data=data,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("exchange", serializer.errors)

    def test_update_feedback_within_window(self):
        """Test updating feedback within update window."""
        feedback = SkillHubTestDataFactory.create_feedback(exchange=self.exchange)

        data = {
            "rating": Decimal("5.0"),
            "comment": "Updated: Absolutely excellent teacher!",
        }

        serializer = SkillFeedbackUpdateSerializer(
            feedback,
            data=data,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
