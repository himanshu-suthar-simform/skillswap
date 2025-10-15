"""
Unit tests for skillhub models.

This module contains comprehensive tests for all skillhub models,
covering model creation, validation, relationships, and edge cases.
"""

from decimal import Decimal

from accounts.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from skillhub.models import Skill
from skillhub.models import SkillCategory
from skillhub.models import SkillExchange
from skillhub.models import SkillFeedback
from skillhub.models import SkillMilestone
from skillhub.models import UserSkill


class SkillCategoryModelTestCase(TestCase):
    """Test cases for the SkillCategory model."""

    def setUp(self):
        """Set up test data."""
        self.category_data = {
            "name": "Programming",
            "description": "Programming and software development skills",
            "icon": "fa-code",
        }

    def test_create_category_with_valid_data(self):
        """Test creating a category with valid data."""
        category = SkillCategory.objects.create(**self.category_data)

        self.assertEqual(category.name, self.category_data["name"])
        self.assertEqual(category.description, self.category_data["description"])
        self.assertEqual(category.icon, self.category_data["icon"])
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_category_name_unique_constraint(self):
        """Test that category name must be unique."""
        SkillCategory.objects.create(**self.category_data)

        with self.assertRaises(IntegrityError):
            SkillCategory.objects.create(**self.category_data)

    def test_category_str_representation(self):
        """Test the string representation of SkillCategory."""
        category = SkillCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), self.category_data["name"])

    def test_category_default_is_active(self):
        """Test that default is_active is True."""
        category = SkillCategory.objects.create(name="Test Category")
        self.assertTrue(category.is_active)

    def test_category_ordering(self):
        """Test that categories are ordered by name."""
        cat1 = SkillCategory.objects.create(name="Zebra")
        cat2 = SkillCategory.objects.create(name="Alpha")

        categories = SkillCategory.objects.all()
        self.assertEqual(categories[0], cat2)
        self.assertEqual(categories[1], cat1)

    def test_get_active_skills_count(self):
        """Test get_active_skills_count method."""
        category = SkillCategory.objects.create(**self.category_data)

        # Create active skills
        Skill.objects.create(
            name="Python",
            category=category,
            description="Python programming",
            is_active=True,
        )
        Skill.objects.create(
            name="Java",
            category=category,
            description="Java programming",
            is_active=True,
        )

        # Create inactive skill
        Skill.objects.create(
            name="C++",
            category=category,
            description="C++ programming",
            is_active=False,
        )

        self.assertEqual(category.get_active_skills_count(), 2)

    def test_category_timestamps(self):
        """Test that timestamps are set correctly."""
        category = SkillCategory.objects.create(**self.category_data)

        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
        self.assertLessEqual(category.created_at, timezone.now())


class SkillModelTestCase(TestCase):
    """Test cases for the Skill model."""

    def setUp(self):
        """Set up test data."""
        self.category = SkillCategory.objects.create(
            name="Programming",
            description="Programming skills",
        )
        self.skill_data = {
            "name": "Python Programming",
            "category": self.category,
            "description": "Learn Python programming from basics to advanced",
        }

    def test_create_skill_with_valid_data(self):
        """Test creating a skill with valid data."""
        skill = Skill.objects.create(**self.skill_data)

        self.assertEqual(skill.name, self.skill_data["name"])
        self.assertEqual(skill.category, self.category)
        self.assertEqual(skill.description, self.skill_data["description"])
        self.assertTrue(skill.is_active)

    def test_skill_name_unique_constraint(self):
        """Test that skill name must be unique."""
        Skill.objects.create(**self.skill_data)

        with self.assertRaises(IntegrityError):
            Skill.objects.create(**self.skill_data)

    def test_skill_str_representation(self):
        """Test the string representation of Skill."""
        skill = Skill.objects.create(**self.skill_data)
        self.assertEqual(str(skill), self.skill_data["name"])

    def test_skill_category_relationship(self):
        """Test the relationship between Skill and SkillCategory."""
        skill = Skill.objects.create(**self.skill_data)

        self.assertEqual(skill.category, self.category)
        self.assertIn(skill, self.category.skills.all())

    def test_skill_category_protect_on_delete(self):
        """Test that deleting category with skills raises error."""
        Skill.objects.create(**self.skill_data)

        with self.assertRaises(Exception):  # ProtectedError
            self.category.delete()

    def test_total_teachers_property(self):
        """Test total_teachers property."""
        skill = Skill.objects.create(**self.skill_data)
        user = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="pass123",
        )

        # Create active user skill
        UserSkill.objects.create(
            user=user,
            skill=skill,
            proficiency_level=UserSkill.ProficiencyLevel.INTERMEDIATE,
            years_of_experience=3,
            learning_outcomes="Learn Python",
            teaching_methods="Online classes",
            estimated_duration=40,
            is_active=True,
        )

        self.assertEqual(skill.total_teachers, 1)

    def test_skill_ordering(self):
        """Test that skills are ordered by name."""
        skill1 = Skill.objects.create(
            name="Zebra Skill",
            category=self.category,
            description="Test description",
        )
        skill2 = Skill.objects.create(
            name="Alpha Skill",
            category=self.category,
            description="Test description",
        )

        skills = Skill.objects.all()
        self.assertEqual(skills[0], skill2)
        self.assertEqual(skills[1], skill1)


class UserSkillModelTestCase(TestCase):
    """Test cases for the UserSkill model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="pass123",
        )
        self.category = SkillCategory.objects.create(name="Programming")
        self.skill = Skill.objects.create(
            name="Python",
            category=self.category,
            description="Python programming",
        )
        self.user_skill_data = {
            "user": self.user,
            "skill": self.skill,
            "proficiency_level": UserSkill.ProficiencyLevel.INTERMEDIATE,
            "years_of_experience": 3,
            "learning_outcomes": "Learn Python basics",
            "teaching_methods": "Online classes",
            "estimated_duration": 40,
        }

    def test_create_user_skill_with_valid_data(self):
        """Test creating a user skill with valid data."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)

        self.assertEqual(user_skill.user, self.user)
        self.assertEqual(user_skill.skill, self.skill)
        self.assertEqual(
            user_skill.proficiency_level,
            UserSkill.ProficiencyLevel.INTERMEDIATE,
        )
        self.assertEqual(user_skill.years_of_experience, 3)
        self.assertTrue(user_skill.is_active)

    def test_user_skill_unique_together_constraint(self):
        """Test that user-skill combination must be unique."""
        UserSkill.objects.create(**self.user_skill_data)

        with self.assertRaises(IntegrityError):
            UserSkill.objects.create(**self.user_skill_data)

    def test_user_skill_str_representation(self):
        """Test the string representation of UserSkill."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)
        expected_str = f"{self.skill.name} by {self.user.email}"
        self.assertEqual(str(user_skill), expected_str)

    def test_user_skill_default_values(self):
        """Test default values for UserSkill."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)

        self.assertTrue(user_skill.is_active)
        self.assertEqual(user_skill.max_students, 1)
        self.assertEqual(user_skill.duration_type, UserSkill.DurationType.HOURS)

    def test_total_students_property(self):
        """Test total_students property."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)
        learner = User.objects.create_user(
            email="learner@example.com",
            username="learner",
            password="pass123",
        )

        SkillExchange.objects.create(
            user_skill=user_skill,
            learner=learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )

        self.assertEqual(user_skill.total_students, 1)

    def test_average_rating_property(self):
        """Test average_rating property."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)
        learner = User.objects.create_user(
            email="learner@example.com",
            username="learner",
            password="pass123",
        )

        exchange = SkillExchange.objects.create(
            user_skill=user_skill,
            learner=learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
            status=SkillExchange.Status.COMPLETED,
        )

        SkillFeedback.objects.create(
            exchange=exchange,
            rating=Decimal("4.5"),
            comment="Great teacher! Very helpful and patient.",
        )

        self.assertEqual(user_skill.average_rating, 4.5)

    def test_success_rate_property(self):
        """Test success_rate property."""
        user_skill = UserSkill.objects.create(**self.user_skill_data)
        learner = User.objects.create_user(
            email="learner@example.com",
            username="learner",
            password="pass123",
        )

        # Create completed exchange
        SkillExchange.objects.create(
            user_skill=user_skill,
            learner=learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
            status=SkillExchange.Status.COMPLETED,
        )

        # Create pending exchange
        learner2 = User.objects.create_user(
            email="learner2@example.com",
            username="learner2",
            password="pass123",
        )
        SkillExchange.objects.create(
            user_skill=user_skill,
            learner=learner2,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
            status=SkillExchange.Status.PENDING,
        )

        self.assertEqual(user_skill.success_rate, 50.0)

    def test_proficiency_level_choices(self):
        """Test proficiency level choices."""
        self.assertEqual(
            UserSkill.ProficiencyLevel.BEGINNER,
            "BEGINNER",
        )
        self.assertEqual(
            UserSkill.ProficiencyLevel.INTERMEDIATE,
            "INTERMEDIATE",
        )
        self.assertEqual(
            UserSkill.ProficiencyLevel.ADVANCED,
            "ADVANCED",
        )
        self.assertEqual(
            UserSkill.ProficiencyLevel.EXPERT,
            "EXPERT",
        )

    def test_duration_type_choices(self):
        """Test duration type choices."""
        self.assertEqual(UserSkill.DurationType.HOURS, "HOURS")
        self.assertEqual(UserSkill.DurationType.DAYS, "DAYS")
        self.assertEqual(UserSkill.DurationType.WEEKS, "WEEKS")
        self.assertEqual(UserSkill.DurationType.MONTHS, "MONTHS")


class SkillMilestoneModelTestCase(TestCase):
    """Test cases for the SkillMilestone model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="pass123",
        )
        self.category = SkillCategory.objects.create(name="Programming")
        self.skill = Skill.objects.create(
            name="Python",
            category=self.category,
            description="Python programming",
        )
        self.user_skill = UserSkill.objects.create(
            user=self.user,
            skill=self.skill,
            proficiency_level=UserSkill.ProficiencyLevel.INTERMEDIATE,
            years_of_experience=3,
            learning_outcomes="Learn Python",
            teaching_methods="Online classes",
            estimated_duration=40,
        )

    def test_create_milestone_with_valid_data(self):
        """Test creating a milestone with valid data."""
        milestone = SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Learn Python Basics",
            description="Variables, data types, control flow",
            order=1,
            estimated_hours=10,
        )

        self.assertEqual(milestone.user_skill, self.user_skill)
        self.assertEqual(milestone.title, "Learn Python Basics")
        self.assertEqual(milestone.order, 1)
        self.assertEqual(milestone.estimated_hours, 10)

    def test_milestone_unique_together_constraint(self):
        """Test that user_skill-order combination must be unique."""
        SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Milestone 1",
            description="Description",
            order=1,
            estimated_hours=10,
        )

        with self.assertRaises(IntegrityError):
            SkillMilestone.objects.create(
                user_skill=self.user_skill,
                title="Milestone 2",
                description="Description",
                order=1,
                estimated_hours=10,
            )

    def test_milestone_str_representation(self):
        """Test the string representation of SkillMilestone."""
        milestone = SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Learn Basics",
            description="Description",
            order=1,
            estimated_hours=10,
        )
        expected_str = f"{self.user_skill} - Milestone 1: Learn Basics"
        self.assertEqual(str(milestone), expected_str)

    def test_milestone_ordering(self):
        """Test that milestones are ordered by user_skill and order."""
        milestone2 = SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Advanced",
            description="Description",
            order=2,
            estimated_hours=20,
        )
        milestone1 = SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Basics",
            description="Description",
            order=1,
            estimated_hours=10,
        )

        milestones = SkillMilestone.objects.all()
        self.assertEqual(milestones[0], milestone1)
        self.assertEqual(milestones[1], milestone2)

    def test_milestone_cascade_delete(self):
        """Test that milestone is deleted when user_skill is deleted."""
        milestone = SkillMilestone.objects.create(
            user_skill=self.user_skill,
            title="Test",
            description="Description",
            order=1,
            estimated_hours=10,
        )
        milestone_id = milestone.id

        self.user_skill.delete()

        with self.assertRaises(SkillMilestone.DoesNotExist):
            SkillMilestone.objects.get(id=milestone_id)


class SkillExchangeModelTestCase(TestCase):
    """Test cases for the SkillExchange model."""

    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="pass123",
        )
        self.learner = User.objects.create_user(
            email="learner@example.com",
            username="learner",
            password="pass123",
        )
        self.category = SkillCategory.objects.create(name="Programming")
        self.skill = Skill.objects.create(
            name="Python",
            category=self.category,
            description="Python programming",
        )
        self.user_skill = UserSkill.objects.create(
            user=self.teacher,
            skill=self.skill,
            proficiency_level=UserSkill.ProficiencyLevel.INTERMEDIATE,
            years_of_experience=3,
            learning_outcomes="Learn Python",
            teaching_methods="Online classes",
            estimated_duration=40,
        )

    def test_create_exchange_with_valid_data(self):
        """Test creating an exchange with valid data."""
        exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python basics",
            availability="Weekends",
            proposed_duration=20,
        )

        self.assertEqual(exchange.user_skill, self.user_skill)
        self.assertEqual(exchange.learner, self.learner)
        self.assertEqual(exchange.status, SkillExchange.Status.PENDING)

    def test_exchange_str_representation(self):
        """Test the string representation of SkillExchange."""
        exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )
        expected_str = f"{self.user_skill} - {self.learner.email} (PENDING)"
        self.assertEqual(str(exchange), expected_str)

    def test_exchange_default_status(self):
        """Test that default status is PENDING."""
        exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )
        self.assertEqual(exchange.status, SkillExchange.Status.PENDING)

    def test_exchange_status_choices(self):
        """Test exchange status choices."""
        self.assertEqual(SkillExchange.Status.PENDING, "PENDING")
        self.assertEqual(SkillExchange.Status.ACCEPTED, "ACCEPTED")
        self.assertEqual(SkillExchange.Status.IN_PROGRESS, "IN_PROGRESS")
        self.assertEqual(SkillExchange.Status.COMPLETED, "COMPLETED")
        self.assertEqual(SkillExchange.Status.CANCELLED, "CANCELLED")

    def test_get_teacher_method(self):
        """Test get_teacher method."""
        exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )
        self.assertEqual(exchange.get_teacher(), self.teacher)

    def test_teacher_property(self):
        """Test teacher property."""
        exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )
        self.assertEqual(exchange.teacher, self.teacher)

    def test_exchange_ordering(self):
        """Test that exchanges are ordered by created_at descending."""
        exchange1 = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )

        learner2 = User.objects.create_user(
            email="learner2@example.com",
            username="learner2",
            password="pass123",
        )
        exchange2 = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=learner2,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
        )

        exchanges = SkillExchange.objects.all()
        self.assertEqual(exchanges[0], exchange2)
        self.assertEqual(exchanges[1], exchange1)


class SkillFeedbackModelTestCase(TestCase):
    """Test cases for the SkillFeedback model."""

    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            username="teacher",
            password="pass123",
        )
        self.learner = User.objects.create_user(
            email="learner@example.com",
            username="learner",
            password="pass123",
        )
        self.category = SkillCategory.objects.create(name="Programming")
        self.skill = Skill.objects.create(
            name="Python",
            category=self.category,
            description="Python programming",
        )
        self.user_skill = UserSkill.objects.create(
            user=self.teacher,
            skill=self.skill,
            proficiency_level=UserSkill.ProficiencyLevel.INTERMEDIATE,
            years_of_experience=3,
            learning_outcomes="Learn Python",
            teaching_methods="Online classes",
            estimated_duration=40,
        )
        self.exchange = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=self.learner,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
            status=SkillExchange.Status.COMPLETED,
        )

    def test_create_feedback_with_valid_data(self):
        """Test creating feedback with valid data."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher! Very helpful and patient.",
        )

        self.assertEqual(feedback.exchange, self.exchange)
        self.assertEqual(feedback.rating, Decimal("4.5"))
        self.assertTrue(feedback.is_recommended)

    def test_feedback_one_to_one_relationship(self):
        """Test one-to-one relationship with exchange."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )

        self.assertEqual(self.exchange.feedback, feedback)

    def test_feedback_str_representation(self):
        """Test the string representation of SkillFeedback."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        expected_str = f"Feedback for {self.user_skill} by {self.learner.email}"
        self.assertEqual(str(feedback), expected_str)

    def test_feedback_default_is_recommended(self):
        """Test that default is_recommended is True."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        self.assertTrue(feedback.is_recommended)

    def test_user_skill_property(self):
        """Test user_skill property."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        self.assertEqual(feedback.user_skill, self.user_skill)

    def test_student_property(self):
        """Test student property."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        self.assertEqual(feedback.student, self.learner)

    def test_is_within_update_window(self):
        """Test is_within_update_window property."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        # Newly created feedback should be within update window
        self.assertTrue(feedback.is_within_update_window)

    def test_feedback_cascade_delete(self):
        """Test that feedback is deleted when exchange is deleted."""
        feedback = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )
        feedback_id = feedback.id

        self.exchange.delete()

        with self.assertRaises(SkillFeedback.DoesNotExist):
            SkillFeedback.objects.get(id=feedback_id)

    def test_feedback_ordering(self):
        """Test that feedback is ordered by created_at descending."""
        feedback1 = SkillFeedback.objects.create(
            exchange=self.exchange,
            rating=Decimal("4.5"),
            comment="Great teacher!",
        )

        # Create another exchange and feedback
        learner2 = User.objects.create_user(
            email="learner2@example.com",
            username="learner2",
            password="pass123",
        )
        exchange2 = SkillExchange.objects.create(
            user_skill=self.user_skill,
            learner=learner2,
            learning_goals="Learn Python",
            availability="Weekends",
            proposed_duration=20,
            status=SkillExchange.Status.COMPLETED,
        )
        feedback2 = SkillFeedback.objects.create(
            exchange=exchange2,
            rating=Decimal("5.0"),
            comment="Excellent!",
        )

        feedbacks = SkillFeedback.objects.all()
        self.assertEqual(feedbacks[0], feedback2)
        self.assertEqual(feedbacks[1], feedback1)
