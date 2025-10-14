from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from general.pagination import LargeResultsSetPagination
from general.pagination import StandardResultsSetPagination
from general.permissions import AdminOrReadOnly
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import SkillCategoryFilter
from .filters import SkillFilter
from .models import Skill
from .models import SkillCategory
from .serializers import SkillCategorySerializer
from .serializers import SkillDetailSerializer
from .serializers import SkillListSerializer


@extend_schema(tags=["Skill Categories"])
class SkillCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skill categories.

    Supports:
    - List categories with filtering and search
    - Create new categories
    - Retrieve category details
    - Update categories
    - Delete categories (soft delete)
    - Toggle category status
    """

    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [AdminOrReadOnly]
    filterset_class = SkillCategoryFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Get the list of categories with optimized queries.
        Annotates the queryset with counts of active skills.
        """
        return self.queryset.annotate(
            active_skills_count=Count("skills", filter=models.Q(skills__is_active=True))
        )

    @extend_schema(
        summary="Toggle category status",
        description="Toggle the active status of a category. Deactivating a category will also deactivate all its skills.",
        responses={
            200: SkillCategorySerializer,
            404: {"description": "Category not found"},
            403: {"description": "Permission denied"},
        },
    )
    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """Toggle the active status of a category."""
        category = self.get_object()
        category.is_active = not category.is_active
        category.save()

        # If category is deactivated, deactivate all its skills
        if not category.is_active:
            category.skills.update(is_active=False)

        return Response(self.get_serializer(category).data)

    def perform_destroy(self, instance):
        """
        Soft delete by deactivating instead of actual deletion.
        This preserves data integrity and history.
        """
        if instance.skills.exists():
            instance.is_active = False
            instance.skills.update(is_active=False)
            instance.save()
        else:
            instance.delete()


@extend_schema(tags=["Skills"])
class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skills.

    Supports:
    - List skills with filtering and search
    - Create new skills
    - Retrieve skill details
    - Update skills
    - Delete skills (soft delete)
    - Toggle skill status
    """

    queryset = Skill.objects.all()
    permission_classes = [AdminOrReadOnly]
    filterset_class = SkillFilter
    pagination_class = LargeResultsSetPagination
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["name", "created_at", "updated_at", "total_teachers"]
    ordering = ["name"]

    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        This optimizes performance by limiting fields in list view.
        """
        if self.action == "list":
            return SkillListSerializer
        return SkillDetailSerializer

    def get_queryset(self):
        """
        Get the list of skills with optimized queries.
        """
        queryset = self.queryset.select_related("category")

        if self.action == "list":
            # Add annotation for list view
            return queryset.annotate(
                total_teachers_count=Count(
                    "teachers", filter=models.Q(teachers__is_active=True)
                )
            )
        # Add prefetch for detail view
        return queryset.prefetch_related("teachers")

    @extend_schema(
        summary="Toggle skill status",
        description="Toggle the active status of a skill.",
        responses={
            200: SkillDetailSerializer,
            404: {"description": "Skill not found"},
            403: {"description": "Permission denied"},
        },
    )
    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """Toggle the active status of a skill."""
        skill = self.get_object()

        # Don't allow activating skill if category is inactive
        if not skill.is_active and not skill.category.is_active:
            return Response(
                {
                    "detail": _(
                        "Cannot activate skill because its category is inactive."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        skill.is_active = not skill.is_active
        skill.save()
        return Response(self.get_serializer(skill).data)

    def perform_destroy(self, instance):
        """
        Soft delete by deactivating instead of actual deletion.
        This preserves data integrity and history.
        """
        if instance.teachers.exists():
            instance.is_active = False
            instance.save()
        else:
            instance.delete()

    @extend_schema(
        summary="Get skills by category",
        description="Get a list of skills filtered by category.",
        parameters=[
            OpenApiParameter(
                name="category_id",
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the category to filter skills by",
            )
        ],
        responses={
            200: SkillListSerializer(many=True),
            404: {"description": "Category not found"},
        },
    )
    @action(
        detail=False, methods=["get"], url_path="by-category/(?P<category_id>[^/.]+)"
    )
    def by_category(self, request, category_id=None):
        """Get skills filtered by category."""
        try:
            category = SkillCategory.objects.get(pk=category_id)
        except SkillCategory.DoesNotExist:
            return Response(
                {"detail": _("Category not found.")}, status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.filter_queryset(self.get_queryset().filter(category=category))
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
