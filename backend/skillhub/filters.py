from django.db import models
from django.db.models import Count
from django_filters import rest_framework as filters

from .models import Skill
from .models import SkillCategory
from .models import UserSkill


class SkillCategoryFilter(filters.FilterSet):
    """
    Filter set for SkillCategory model.

    Filters:
    - name: Case-insensitive partial match
    - is_active: Boolean filter
    - created_after: Filter categories created after given date
    - created_before: Filter categories created before given date
    - has_skills: Boolean filter for categories with/without active skills
    """

    name = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    has_skills = filters.BooleanFilter(method="filter_has_skills")

    class Meta:
        model = SkillCategory
        fields = ["name", "is_active"]

    def filter_has_skills(self, queryset, name, value):
        """Filter categories based on whether they have active skills."""
        queryset = queryset.annotate(
            active_skills_count=Count("skills", filter=models.Q(skills__is_active=True))
        )
        return (
            queryset.filter(active_skills_count__gt=0)
            if value
            else queryset.filter(active_skills_count=0)
        )


class SkillFilter(filters.FilterSet):
    """
    Filter set for Skill model.

    Filters:
    - name: Case-insensitive partial match
    - category: Filter by category ID
    - category_name: Case-insensitive partial match on category name
    - is_active: Boolean filter
    - created_after: Filter skills created after given date
    - created_before: Filter skills created before given date
    - has_teachers: Boolean filter for skills with/without active teachers
    - min_teachers: Filter skills with minimum number of active teachers
    """

    name = filters.CharFilter(lookup_expr="icontains")
    category = filters.NumberFilter()
    category_name = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    is_active = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    has_teachers = filters.BooleanFilter(method="filter_has_teachers")
    min_teachers = filters.NumberFilter(method="filter_min_teachers")

    class Meta:
        model = Skill
        fields = ["name", "category", "is_active"]

    def filter_has_teachers(self, queryset, name, value):
        """Filter skills based on whether they have active teachers."""
        queryset = queryset.annotate(
            active_teachers_count=Count(
                "teachers", filter=models.Q(teachers__is_active=True)
            )
        )
        return (
            queryset.filter(active_teachers_count__gt=0)
            if value
            else queryset.filter(active_teachers_count=0)
        )

    def filter_min_teachers(self, queryset, name, value):
        """Filter skills based on minimum number of active teachers."""
        return queryset.annotate(
            active_teachers_count=Count(
                "teachers", filter=models.Q(teachers__is_active=True)
            )
        ).filter(active_teachers_count__gte=value)


class UserSkillFilter(filters.FilterSet):
    """
    Filter set for UserSkill model.

    Filters:
    - skill: Filter by skill ID
    - category: Filter by category ID
    - user: Filter by user ID
    - is_active: Boolean filter
    - min_rating: Filter by minimum rating
    - min_experience: Filter by minimum years of experience
    - proficiency_level: Filter by exact proficiency level
    - min_proficiency: Filter by minimum proficiency level
    - has_students: Boolean filter for skills with/without students
    - min_students: Filter by minimum number of students
    - price_range: Filter by hourly rate range
    - created_after: Filter skills created after given date
    - created_before: Filter skills created before given date
    """

    skill = filters.NumberFilter()
    category = filters.NumberFilter(field_name="skill__category")
    user = filters.NumberFilter()
    is_active = filters.BooleanFilter()

    min_rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    min_experience = filters.NumberFilter(
        field_name="years_of_experience", lookup_expr="gte"
    )

    proficiency_level = filters.ChoiceFilter(choices=UserSkill.ProficiencyLevel.choices)
    min_proficiency = filters.NumberFilter(method="filter_min_proficiency")

    has_students = filters.BooleanFilter(method="filter_has_students")
    min_students = filters.NumberFilter(method="filter_min_students")

    price_min = filters.NumberFilter(field_name="hourly_rate", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="hourly_rate", lookup_expr="lte")

    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = UserSkill
        fields = [
            "skill",
            "category",
            "user",
            "is_active",
            "proficiency_level",
        ]

    def filter_min_proficiency(self, queryset, name, value):
        """Filter based on minimum proficiency level."""
        proficiency_order = dict(UserSkill.ProficiencyLevel.choices)
        min_level = [k for k, v in proficiency_order.items() if int(k) >= value]
        return queryset.filter(proficiency_level__in=min_level)

    def filter_has_students(self, queryset, name, value):
        """Filter skills based on whether they have students."""
        queryset = queryset.annotate(total_students=Count("exchanges", distinct=True))
        return (
            queryset.filter(total_students__gt=0)
            if value
            else queryset.filter(total_students=0)
        )

    def filter_min_students(self, queryset, name, value):
        """Filter skills based on minimum number of students."""
        return queryset.annotate(
            total_students=Count("exchanges", distinct=True)
        ).filter(total_students__gte=value)
