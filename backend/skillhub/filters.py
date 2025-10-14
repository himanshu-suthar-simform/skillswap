from django.db import models
from django.db.models import Count
from django_filters import rest_framework as filters

from .models import Skill
from .models import SkillCategory


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
