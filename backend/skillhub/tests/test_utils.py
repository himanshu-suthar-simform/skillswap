"""
Utility functions and helpers for skillhub tests.

This module provides reusable test utilities, fixtures, and helper functions
to reduce code duplication and improve test maintainability.
"""

from decimal import Decimal
from typing import Dict
from typing import Optional

from accounts.models import User
from skillhub.models import Skill
from skillhub.models import SkillCategory
from skillhub.models import SkillExchange
from skillhub.models import SkillFeedback
from skillhub.models import SkillMilestone
from skillhub.models import UserSkill


class SkillHubTestDataFactory:
    """Factory class for creating skillhub test data."""

    @staticmethod
    def create_user(
        email: str = "testuser@example.com",
        username: str = "testuser",
        password: str = "testpass123",
        is_active: bool = True,
        **kwargs
    ) -> User:
        """Create a test user."""
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_active=is_active,
            **kwargs
        )

    @staticmethod
    def create_category(
        name: str = "Programming",
        description: str = "Programming skills",
        icon: str = "fa-code",
        is_active: bool = True,
        **kwargs
    ) -> SkillCategory:
        """Create a test skill category."""
        category, _ = SkillCategory.objects.get_or_create(
            name=name, description=description, icon=icon, is_active=is_active, **kwargs
        )
        return category

    @staticmethod
    def create_skill(
        name: str = "Python Programming",
        category: Optional[SkillCategory] = None,
        description: str = "Learn Python programming",
        is_active: bool = True,
        **kwargs
    ) -> Skill:
        """Create a test skill."""
        if category is None:
            category = SkillHubTestDataFactory.create_category()

        skill, _ = Skill.objects.get_or_create(
            name=name,
            category=category,
            description=description,
            is_active=is_active,
            **kwargs
        )
        return skill

    @staticmethod
    def create_user_skill(
        user: Optional[User] = None,
        skill: Optional[Skill] = None,
        proficiency_level: str = UserSkill.ProficiencyLevel.INTERMEDIATE,
        years_of_experience: int = 3,
        learning_outcomes: str = "Learn the skill",
        teaching_methods: str = "Online classes",
        estimated_duration: int = 40,
        is_active: bool = True,
        **kwargs
    ) -> UserSkill:
        """Create a test user skill."""
        if user is None:
            user = SkillHubTestDataFactory.create_user()
        if skill is None:
            skill = SkillHubTestDataFactory.create_skill()

        return UserSkill.objects.create(
            user=user,
            skill=skill,
            proficiency_level=proficiency_level,
            years_of_experience=years_of_experience,
            learning_outcomes=learning_outcomes,
            teaching_methods=teaching_methods,
            estimated_duration=estimated_duration,
            is_active=is_active,
            **kwargs
        )

    @staticmethod
    def create_milestone(
        user_skill: Optional[UserSkill] = None,
        title: str = "Milestone 1",
        description: str = "Complete this milestone",
        order: int = 1,
        estimated_hours: int = 10,
        **kwargs
    ) -> SkillMilestone:
        """Create a test milestone."""
        if user_skill is None:
            user_skill = SkillHubTestDataFactory.create_user_skill()

        return SkillMilestone.objects.create(
            user_skill=user_skill,
            title=title,
            description=description,
            order=order,
            estimated_hours=estimated_hours,
            **kwargs
        )

    @staticmethod
    def create_exchange(
        user_skill: Optional[UserSkill] = None,
        learner: Optional[User] = None,
        learning_goals: str = "Learn the skill",
        availability: str = "Weekends",
        proposed_duration: int = 20,
        status: str = SkillExchange.Status.PENDING,
        **kwargs
    ) -> SkillExchange:
        """Create a test skill exchange."""
        if user_skill is None:
            user_skill = SkillHubTestDataFactory.create_user_skill()
        if learner is None:
            learner = SkillHubTestDataFactory.create_user(
                email="learner@example.com",
                username="learner",
            )

        return SkillExchange.objects.create(
            user_skill=user_skill,
            learner=learner,
            learning_goals=learning_goals,
            availability=availability,
            proposed_duration=proposed_duration,
            status=status,
            **kwargs
        )

    @staticmethod
    def create_feedback(
        exchange: Optional[SkillExchange] = None,
        rating: Decimal = Decimal("4.5"),
        comment: str = "Great teacher! Very helpful and patient.",
        is_recommended: bool = True,
        **kwargs
    ) -> SkillFeedback:
        """Create a test feedback."""
        if exchange is None:
            exchange = SkillHubTestDataFactory.create_exchange(
                status=SkillExchange.Status.COMPLETED
            )

        return SkillFeedback.objects.create(
            exchange=exchange,
            rating=rating,
            comment=comment,
            is_recommended=is_recommended,
            **kwargs
        )


class SkillHubAssertionHelpers:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_category_data_matches(
        test_case, category_data: Dict, category: SkillCategory
    ):
        """Assert that category data matches category instance."""
        test_case.assertEqual(category_data.get("name"), category.name)
        if "description" in category_data:
            test_case.assertEqual(category_data["description"], category.description)
        if "icon" in category_data:
            test_case.assertEqual(category_data["icon"], category.icon)

    @staticmethod
    def assert_skill_data_matches(test_case, skill_data: Dict, skill: Skill):
        """Assert that skill data matches skill instance."""
        test_case.assertEqual(skill_data.get("name"), skill.name)
        if "description" in skill_data:
            test_case.assertEqual(skill_data["description"], skill.description)

    @staticmethod
    def assert_user_skill_data_matches(
        test_case, user_skill_data: Dict, user_skill: UserSkill
    ):
        """Assert that user skill data matches user skill instance."""
        if "proficiency_level" in user_skill_data:
            test_case.assertEqual(
                user_skill_data["proficiency_level"], user_skill.proficiency_level
            )
        if "years_of_experience" in user_skill_data:
            test_case.assertEqual(
                user_skill_data["years_of_experience"], user_skill.years_of_experience
            )


def create_authenticated_client(user: User):
    """Create an authenticated API client for testing."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=user)
    return client
