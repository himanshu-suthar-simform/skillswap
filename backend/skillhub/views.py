from django.db import models
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from general.pagination import LargeResultsSetPagination
from general.pagination import StandardResultsSetPagination
from general.permissions import AdminOrReadOnly
from general.permissions import IsOwnerOrAdmin
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import SkillCategoryFilter
from .filters import SkillFilter
from .filters import UserSkillFilter
from .models import Skill
from .models import SkillCategory
from .models import SkillMilestone
from .models import UserSkill
from .serializers import SkillCategorySerializer
from .serializers import SkillDetailSerializer
from .serializers import SkillListSerializer
from .serializers import SkillMilestoneSerializer
from .serializers import UserSkillDetailSerializer
from .serializers import UserSkillListSerializer


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


@extend_schema(tags=["User Skills"])
class UserSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user's teaching skills.

    Supports:
    - List user's teaching skills with filtering and search
    - Create new teaching skill offering
    - Retrieve teaching skill details
    - Update teaching skill information
    - Delete teaching skill
    - Toggle skill availability
    - Manage skill milestones
    """

    permission_classes = [IsOwnerOrAdmin]
    pagination_class = StandardResultsSetPagination
    filterset_class = UserSkillFilter
    search_fields = [
        "skill__name",
        "skill__description",
        "skill__category__name",
        "user__username",
        "user__email",
    ]
    ordering_fields = [
        "created_at",
        "proficiency_level",
        "years_of_experience",
        "student_count",
        "rating",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Get the list of user skills with optimized queries.
        Filter based on user permissions and annotate with stats.
        """
        queryset = UserSkill.objects.select_related("user", "skill", "skill__category")

        # For non-admin users, show only active skills of others
        if not (
            self.request.user.role == "ADMIN"
            or self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                models.Q(is_active=True) | models.Q(user=self.request.user)
            )

        # For milestone-related actions, only include basic relations
        if self.action in [
            "add_milestone",
            "update_milestone",
            "delete_milestone",
            "reorder_milestones",
        ]:
            return queryset.prefetch_related(
                Prefetch(
                    "milestones",
                    queryset=SkillMilestone.objects.order_by("order"),
                )
            )

        # Add annotations based on action
        if self.action == "list":
            queryset = queryset.annotate(
                student_count=Count("exchanges", distinct=True),
                rating=Avg("feedback_received__rating"),
            )
        else:
            # For detail view, add more annotations and prefetch related data
            queryset = queryset.prefetch_related(
                Prefetch(
                    "milestones",
                    queryset=SkillMilestone.objects.order_by("order"),
                ),
                "feedback_received",
                "exchanges",
            ).annotate(
                student_count=Count("exchanges", distinct=True),
                completed_count=Count(
                    "exchanges",
                    filter=models.Q(exchanges__status="COMPLETED"),
                    distinct=True,
                ),
                rating=Avg("feedback_received__rating"),
                # Calculate success rate using ExpressionWrapper to avoid division by zero
                _success_rate=models.ExpressionWrapper(
                    models.Case(
                        models.When(
                            student_count__gt=0,
                            then=100.0
                            * models.F("completed_count")
                            / models.F("student_count"),
                        ),
                        default=0.0,
                        output_field=models.DecimalField(
                            max_digits=5, decimal_places=2
                        ),
                    ),
                    output_field=models.DecimalField(max_digits=5, decimal_places=2),
                ),
            )

        return queryset

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == "list":
            return UserSkillListSerializer
        return UserSkillDetailSerializer

    def perform_create(self, serializer):
        """Create a new teaching skill for the current user."""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Toggle skill availability",
        description="Toggle whether the skill is currently available for teaching.",
        responses={
            200: UserSkillDetailSerializer,
            404: {"description": "Skill not found"},
            403: {"description": "Permission denied"},
        },
    )
    @action(detail=True, methods=["post"])
    def toggle_availability(self, request, pk=None):
        """Toggle the active status of a teaching skill."""
        user_skill = self.get_object()

        # Don't allow activation if skill or category is inactive
        if not user_skill.is_active and (
            not user_skill.skill.is_active or not user_skill.skill.category.is_active
        ):
            return Response(
                {
                    "detail": _(
                        "Cannot activate teaching skill because the skill or its category is inactive."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_skill.is_active = not user_skill.is_active
        user_skill.save()
        return Response(self.get_serializer(user_skill).data)

    @extend_schema(
        summary="Add milestone",
        description="Add a new milestone to the teaching skill.",
        request=SkillMilestoneSerializer,
        responses={
            201: SkillMilestoneSerializer,
            400: {"description": "Invalid data"},
            404: {"description": "Skill not found"},
        },
    )
    @action(detail=True, methods=["post"])
    def add_milestone(self, request, pk=None):
        """Add a new milestone to the teaching skill."""
        user_skill = self.get_object()

        # Add user_skill to serializer context
        serializer = SkillMilestoneSerializer(
            data=request.data,
            context={"user_skill": user_skill},
        )
        serializer.is_valid(raise_exception=True)

        serializer.save(user_skill=user_skill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update milestone",
        description="Update an existing milestone.",
        parameters=[
            OpenApiParameter(
                name="milestone_id",
                location=OpenApiParameter.PATH,
                type=int,
                description="ID of the milestone to update",
            ),
        ],
        request=SkillMilestoneSerializer,
        responses={
            200: SkillMilestoneSerializer,
            404: {"description": "Milestone not found"},
        },
    )
    @action(
        detail=True,
        methods=["put", "patch"],
        url_path="milestone/(?P<milestone_id>[^/.]+)",
    )
    def update_milestone(self, request, pk=None, milestone_id=None):
        """Update a specific milestone."""
        user_skill = self.get_object()

        try:
            milestone = user_skill.milestones.get(id=milestone_id)
        except SkillMilestone.DoesNotExist:
            return Response(
                {"detail": _("Milestone not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SkillMilestoneSerializer(
            milestone,
            data=request.data,
            context={"user_skill": user_skill},
            partial=request.method == "PATCH",
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(
        summary="Delete milestone",
        description="Delete a milestone from the teaching skill.",
        parameters=[
            OpenApiParameter(
                name="milestone_id",
                location=OpenApiParameter.PATH,
                type=int,
                description="ID of the milestone to delete",
            ),
        ],
        responses={
            204: {"description": "Milestone deleted"},
            404: {"description": "Milestone not found"},
        },
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="milestone/(?P<milestone_id>[^/.]+)",
    )
    def delete_milestone(self, request, pk=None, milestone_id=None):
        """Delete a specific milestone."""
        user_skill = self.get_object()

        try:
            milestone = user_skill.milestones.get(id=milestone_id)
        except SkillMilestone.DoesNotExist:
            return Response(
                {"detail": _("Milestone not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        milestone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Reorder milestones",
        description="Update the order of milestones for this teaching skill.",
        request={
            "type": "object",
            "properties": {
                "orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "order": {"type": "integer"},
                        },
                    },
                },
            },
        },
        responses={
            200: SkillMilestoneSerializer(many=True),
            400: {"description": "Invalid data"},
        },
    )
    @action(detail=True, methods=["post"])
    def reorder_milestones(self, request, pk=None):
        """Reorder milestones of the teaching skill."""
        user_skill = self.get_object()

        orders = request.data.get("orders", [])
        if not isinstance(orders, list):
            raise ValidationError({"orders": _("Must be a list of orders.")})

        milestone_dict = {m.id: m for m in user_skill.milestones.all()}
        used_orders = set()

        # Validate the orders
        for item in orders:
            if not isinstance(item, dict):
                raise ValidationError(
                    _("Each item must be an object with 'id' and 'order'.")
                )

            milestone_id = item.get("id")
            order = item.get("order")

            if not milestone_id or not order:
                raise ValidationError(_("Each item must have both 'id' and 'order'."))

            if order in used_orders:
                raise ValidationError(_("Duplicate order values are not allowed."))

            if milestone_id not in milestone_dict:
                raise ValidationError(_(f"Milestone with id {milestone_id} not found."))

            used_orders.add(order)

        # Update the orders
        for item in orders:
            milestone = milestone_dict[item["id"]]
            milestone.order = item["order"]
            milestone.save()

        # Return updated milestones
        milestones = user_skill.milestones.all().order_by("order")
        serializer = SkillMilestoneSerializer(milestones, many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        """
        Soft delete if there are associated records.
        Hard delete if no associated records exist.
        """
        if instance.exchanges.exists() or instance.feedback_received.exists():
            instance.is_active = False
            instance.save()
        else:
            instance.delete()
