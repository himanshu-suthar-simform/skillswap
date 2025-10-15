from decimal import Decimal

from accounts.serializers import UserBasicSerializer
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Skill
from .models import SkillCategory
from .models import SkillExchange
from .models import SkillFeedback
from .models import SkillMilestone
from .models import UserSkill


class SkillCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SkillCategory model.
    Handles both read and write operations.
    """

    skills_count = serializers.IntegerField(
        source="get_active_skills_count", read_only=True
    )

    class Meta:
        model = SkillCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "is_active",
            "skills_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        """
        Validate category name:
        - Check for uniqueness case-insensitively
        - Ensure reasonable length
        - No special characters except spaces and hyphens
        """
        # Case-insensitive uniqueness check
        if (
            SkillCategory.objects.filter(name__iexact=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                _("A category with this name already exists.")
            )

        # Length check
        if len(value) < 3:
            raise serializers.ValidationError(
                _("Category name must be at least 3 characters long.")
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                _("Category name cannot exceed 100 characters.")
            )

        # Character validation
        if not value.replace(" ", "").replace("-", "").isalnum():
            raise serializers.ValidationError(
                _(
                    "Category name can only contain letters, numbers, spaces, and hyphens."
                )
            )

        return value.strip()

    def validate_icon(self, value):
        """Validate icon class name."""
        if value and not value.replace("-", "").replace("_", "").isalnum():
            raise serializers.ValidationError(
                _(
                    "Icon class can only contain letters, numbers, hyphens, and underscores."
                )
            )
        return value.strip() if value else ""


class SkillListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Skills.
    Used in list view for optimized performance.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)
    total_teachers = serializers.IntegerField(
        source="total_teachers_count", read_only=True
    )

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "is_active",
            "total_teachers",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class SkillDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Skill information.
    Used in retrieve, create, and update operations.
    """

    category_details = SkillCategorySerializer(source="category", read_only=True)
    total_teachers = serializers.IntegerField(
        source="total_teachers_count", read_only=True
    )

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "category",
            "category_details",
            "description",
            "is_active",
            "total_teachers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        """
        Validate skill name:
        - Check for uniqueness case-insensitively
        - Ensure reasonable length
        - Allow common special characters
        """
        # Case-insensitive uniqueness check
        if (
            Skill.objects.filter(name__iexact=value)
            .exclude(id=self.instance.id if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                _("A skill with this name already exists.")
            )

        # Length check
        if len(value) < 3:
            raise serializers.ValidationError(
                _("Skill name must be at least 3 characters long.")
            )
        if len(value) > 200:
            raise serializers.ValidationError(
                _("Skill name cannot exceed 200 characters.")
            )

        # Basic character validation (allowing more special characters than categories)
        if not all(c.isalnum() or c in " -+#.()" for c in value):
            raise serializers.ValidationError(
                _(
                    "Skill name can only contain letters, numbers, spaces, and basic punctuation (-.+#())."
                )
            )

        return value.strip()

    def validate_description(self, value):
        """
        Validate skill description:
        - Ensure minimum length for meaningful description
        - Check for maximum length
        - Basic content validation
        """
        # Length checks
        if len(value.strip()) < 50:
            raise serializers.ValidationError(
                _("Description must be at least 50 characters long.")
            )
        if len(value) > 5000:
            raise serializers.ValidationError(
                _("Description cannot exceed 5000 characters.")
            )

        # Basic content validation
        if value.lower().count("http") > 5:
            raise serializers.ValidationError(
                _(
                    "Description contains too many URLs. Please keep it concise and relevant."
                )
            )

        return value.strip()

    def validate(self, data):
        """
        Cross-field validation:
        - Ensure category is active when creating/updating an active skill
        """
        category = data.get(
            "category", self.instance.category if self.instance else None
        )

        if data.get("is_active", True) and (category and not category.is_active):
            raise serializers.ValidationError(
                {
                    "category": _(
                        "Cannot create/update an active skill in an inactive category."
                    )
                }
            )

        return data


class SkillMilestoneSerializer(serializers.ModelSerializer):
    """
    Serializer for SkillMilestone model.
    Used in both list and detail views of UserSkill.
    """

    class Meta:
        model = SkillMilestone
        fields = [
            "id",
            "title",
            "description",
            "order",
            "estimated_hours",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_order(self, value):
        """Ensure order is unique within a user_skill."""
        user_skill = self.context["user_skill"]
        if SkillMilestone.objects.filter(user_skill=user_skill, order=value).exists():
            raise serializers.ValidationError(
                _("A milestone with this order number already exists.")
            )
        return value


class UserSkillListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing UserSkills.
    Includes basic information and stats.
    """

    skill_name = serializers.CharField(source="skill.name", read_only=True)
    category_name = serializers.CharField(source="skill.category.name", read_only=True)
    student_count = serializers.IntegerField(source="total_students", read_only=True)
    rating = serializers.DecimalField(
        source="average_rating",
        read_only=True,
        max_digits=3,
        decimal_places=2,
    )

    class Meta:
        model = UserSkill
        fields = [
            "id",
            "skill",
            "skill_name",
            "category_name",
            "proficiency_level",
            "is_active",
            "student_count",
            "rating",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class UserSkillDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed UserSkill view.
    Includes all fields and related information.
    """

    skill_details = SkillDetailSerializer(source="skill", read_only=True)
    student_count = serializers.IntegerField(source="total_students", read_only=True)
    rating = serializers.DecimalField(
        source="average_rating",
        read_only=True,
        max_digits=3,
        decimal_places=2,
    )
    success_rate = serializers.DecimalField(
        source="_success_rate",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    milestones = SkillMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = UserSkill
        fields = [
            "id",
            "skill",
            "skill_details",
            "user",
            "proficiency_level",
            "years_of_experience",
            "certifications",
            "portfolio_links",
            "prerequisites",
            "learning_outcomes",
            "teaching_methods",
            "estimated_duration",
            "duration_type",
            "is_active",
            "max_students",
            "available_time_slots",
            "student_count",
            "rating",
            "success_rate",
            "milestones",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_skill(self, value):
        """
        Validate skill:
        - Ensure skill is active
        - Check for duplicate teaching registration
        """
        request = self.context["request"]
        if not value.is_active:
            raise serializers.ValidationError(_("This skill is not currently active."))

        if not value.category.is_active:
            raise serializers.ValidationError(
                _("This skill's category is not currently active.")
            )

        # Check for existing user_skill on update
        if (
            UserSkill.objects.exclude(id=self.instance.id if self.instance else None)
            .filter(user=request.user, skill=value)
            .exists()
        ):
            raise serializers.ValidationError(
                _("You are already registered to teach this skill.")
            )

        return value

    def validate(self, data):
        """
        Cross-field validation:
        - Ensure reasonable estimated_duration for duration_type
        - Validate time slot format
        """
        if "estimated_duration" in data and "duration_type" in data:
            duration = data["estimated_duration"]
            duration_type = data["duration_type"]

            max_durations = {
                "HOURS": 72,  # Max 3 days
                "DAYS": 90,  # Max 3 months
                "WEEKS": 52,  # Max 1 year
                "MONTHS": 12,  # Max 1 year
            }

            if duration > max_durations[duration_type]:
                raise serializers.ValidationError(
                    {
                        "estimated_duration": _(
                            f"Duration cannot exceed {max_durations[duration_type]} {duration_type.lower()}"
                        )
                    }
                )

        return data

    def create(self, validated_data):
        """Create UserSkill with current user."""
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class SkillExchangeListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing skill exchange requests.
    Shows basic information needed for list views.
    """

    teacher_skill = serializers.SerializerMethodField()
    learner = UserBasicSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SkillExchange
        fields = [
            "id",
            "user_skill",
            "teacher_skill",
            "learner",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "teacher_name": {"type": "string"},
                "skill_name": {"type": "string"},
                "proficiency_level": {"type": "string"},
            },
        }
    )
    def get_teacher_skill(self, obj):
        """Get basic information about the teacher's skill."""
        return {
            "teacher_name": obj.user_skill.user.get_full_name()
            or obj.user_skill.user.email,
            "skill_name": obj.user_skill.skill.name,
            "proficiency_level": obj.user_skill.get_proficiency_level_display(),
        }


class SkillExchangeStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating skill exchange status."""

    status = serializers.ChoiceField(
        choices=SkillExchange.Status.choices, help_text=_("New status for the exchange")
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=_(
            "Required reason when cancelling, optional for other status changes"
        ),
    )

    def validate(self, data):
        """Validate that reason is provided when status is CANCELLED."""
        status = data.get("status")
        reason = data.get("reason")

        if status == SkillExchange.Status.CANCELLED:
            if not reason:
                raise serializers.ValidationError(
                    {"reason": _("Reason is required when cancelling an exchange.")}
                )
            if len(reason.strip()) < 10:
                raise serializers.ValidationError(
                    {
                        "reason": _(
                            "Please provide a more detailed reason for cancellation (at least 10 characters)."
                        )
                    }
                )

        return data


class SkillExchangeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed skill exchange information.
    Used for create, retrieve, and update operations.
    """

    teacher_skill = UserSkillDetailSerializer(source="user_skill", read_only=True)
    learner = UserBasicSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    offered_skill = serializers.PrimaryKeyRelatedField(
        queryset=UserSkill.objects.all(),
        required=False,
        write_only=True,
        help_text=_("The skill offered by the learner in exchange (optional)"),
    )

    class Meta:
        model = SkillExchange
        fields = [
            "id",
            "user_skill",
            "teacher_skill",
            "learner",
            "offered_skill",
            "status",
            "status_display",
            "learning_goals",
            "availability",
            "proposed_duration",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "learner", "created_at", "updated_at"]

    def validate_user_skill(self, value):
        """
        Validate the requested teaching skill:
        - Must be active
        - Can't request your own skill
        - Teacher must be available
        """
        request = self.context["request"]

        if not value.is_active:
            raise serializers.ValidationError(
                _("This skill is not currently available for teaching.")
            )

        if value.user == request.user:
            raise serializers.ValidationError(
                _("You cannot request to learn your own teaching skill.")
            )

        # Check if teacher has reached maximum students
        active_exchanges = value.exchanges.filter(
            status__in=["ACCEPTED", "IN_PROGRESS"]
        ).count()
        if active_exchanges >= value.max_students:
            raise serializers.ValidationError(
                _("This teacher has reached their maximum number of students.")
            )

        return value

    def validate_offered_skill(self, value):
        """
        Validate the offered skill:
        - Must be active
        - Must belong to the requesting user
        """
        if value:
            request = self.context["request"]

            if value.user != request.user:
                raise serializers.ValidationError(
                    _("You can only offer your own teaching skills.")
                )

            if not value.is_active:
                raise serializers.ValidationError(
                    _("The skill you're offering is not currently active.")
                )

        return value

    def validate(self, data):
        """
        Cross-field validation:
        - Ensure reasonable proposed duration
        - Basic availability format check
        - Prevent duplicate active requests
        """
        # Validate proposed duration (between 1 hour and 6 months)
        if data.get("proposed_duration", 0) > 1000:
            raise serializers.ValidationError(
                {"proposed_duration": _("Proposed duration seems unreasonably long.")}
            )

        # Ensure availability is provided and has reasonable length
        availability = data.get("availability", "").strip()
        if not availability:
            raise serializers.ValidationError(
                {"availability": _("You must provide your availability.")}
            )
        if len(availability) < 10:
            raise serializers.ValidationError(
                {
                    "availability": _(
                        "Please provide more detailed availability information."
                    )
                }
            )

        # Check for duplicate active requests
        request = self.context["request"]
        user_skill = data.get("user_skill")

        if self.instance is None:  # Only check on create
            existing_request = SkillExchange.objects.filter(
                user_skill=user_skill,
                learner=request.user,
                status__in=["PENDING", "ACCEPTED", "IN_PROGRESS"],
            ).exists()

            if existing_request:
                raise serializers.ValidationError(
                    _("You already have an active request for this skill.")
                )

        return data

    def create(self, validated_data):
        """Create exchange request with current user as learner."""
        request = self.context["request"]
        # Remove offered_skill as it's not a model field
        validated_data.pop("offered_skill", None)
        validated_data["learner"] = request.user
        validated_data["status"] = SkillExchange.Status.PENDING
        return super().create(validated_data)


class SkillFeedbackListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing feedback.
    Includes basic information needed for list views.
    """

    teacher_name = serializers.CharField(
        source="exchange.user_skill.user.get_full_name"
    )
    student_name = serializers.CharField(source="exchange.learner.get_full_name")
    skill_name = serializers.CharField(source="exchange.user_skill.skill.name")
    days_ago = serializers.SerializerMethodField()

    class Meta:
        model = SkillFeedback
        fields = [
            "id",
            "teacher_name",
            "student_name",
            "skill_name",
            "rating",
            "is_recommended",
            "days_ago",
            "created_at",
        ]
        read_only_fields = fields

    @extend_schema_field(
        {"type": "integer", "description": "Number of days since feedback was given"}
    )
    def get_days_ago(self, obj):
        """Calculate days since feedback was given."""
        delta = timezone.now() - obj.created_at
        return delta.days


class SkillFeedbackDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed feedback view.
    Used for retrieving complete feedback information.
    """

    teacher_skill = UserSkillListSerializer(
        source="exchange.user_skill", read_only=True
    )
    student_name = serializers.CharField(
        source="exchange.learner.get_full_name", read_only=True
    )
    is_within_update_window = serializers.BooleanField(read_only=True)
    days_ago = serializers.SerializerMethodField()
    exchange_details = SkillExchangeListSerializer(source="exchange", read_only=True)

    class Meta:
        model = SkillFeedback
        fields = [
            "id",
            "exchange",
            "exchange_details",
            "teacher_skill",
            "student_name",
            "rating",
            "comment",
            "is_recommended",
            "days_ago",
            "is_within_update_window",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "exchange",
            "created_at",
            "updated_at",
            "is_within_update_window",
            "days_ago",
        ]

    @extend_schema_field(
        {"type": "integer", "description": "Number of days since feedback was given"}
    )
    def get_days_ago(self, obj):
        """Calculate days since feedback was given."""
        delta = timezone.now() - obj.created_at
        return delta.days


class SkillFeedbackCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new feedback.
    Includes validation for exchange-based feedback creation.
    """

    exchange = serializers.PrimaryKeyRelatedField(
        queryset=SkillExchange.objects.filter(status=SkillExchange.Status.COMPLETED),
        help_text=_("The completed exchange for which feedback is being given."),
    )

    class Meta:
        model = SkillFeedback
        fields = [
            "exchange",
            "rating",
            "comment",
            "is_recommended",
        ]

    def validate_exchange(self, value):
        """
        Validate that:
        1. Exchange is completed
        2. No existing feedback
        3. Current user is the learner
        """
        if value.status != SkillExchange.Status.COMPLETED:
            raise serializers.ValidationError(
                _("Can only provide feedback for completed exchanges.")
            )

        if hasattr(value, "feedback"):
            raise serializers.ValidationError(
                _("Feedback has already been provided for this exchange.")
            )

        if value.learner != self.context["request"].user:
            raise serializers.ValidationError(
                _(
                    "You can only provide feedback for exchanges where you were the learner."
                )
            )

        return value

    def validate_rating(self, value):
        """
        Validate rating:
        - Must be between 0 and 5
        - Must be in 0.5 increments
        """

        if value is None:
            return value

        try:
            value = Decimal(str(value))
        except (TypeError, ValueError):
            raise serializers.ValidationError(_("Rating must be a valid number."))

        if not (Decimal("0") <= value <= Decimal("5")):
            raise serializers.ValidationError(_("Rating must be between 0 and 5."))

        if value * 2 != int(value * 2):
            raise serializers.ValidationError(_("Rating must be in 0.5 increments."))

        return value

    def validate_comment(self, value):
        """
        Validate comment:
        - Minimum length for meaningful feedback
        - Maximum length to prevent abuse
        - Basic content validation
        """
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                _("Please provide at least 20 characters of feedback.")
            )

        if len(value) > 2000:
            raise serializers.ValidationError(
                _("Feedback comment cannot exceed 2000 characters.")
            )

        # Basic content validation (e.g., no excessive URLs, no HTML)
        if value.lower().count("http") > 2:
            raise serializers.ValidationError(
                _("Too many URLs in the feedback. Maximum 2 URLs allowed.")
            )

        if "<" in value and ">" in value:
            raise serializers.ValidationError(
                _("HTML tags are not allowed in feedback.")
            )

        return value.strip()


class SkillFeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing feedback.
    Includes validation for update window and field restrictions.
    """

    class Meta:
        model = SkillFeedback
        fields = [
            "rating",
            "comment",
            "is_recommended",
        ]

    def validate_rating(self, value):
        """
        Validate rating:
        - Must be between 0 and 5
        - Must be in 0.5 increments
        """
        from decimal import Decimal

        if value is None:
            return value

        try:
            value = Decimal(str(value))
        except (TypeError, ValueError):
            raise serializers.ValidationError(_("Rating must be a valid number."))

        if not (Decimal("0") <= value <= Decimal("5")):
            raise serializers.ValidationError(_("Rating must be between 0 and 5."))

        if value * 2 != int(value * 2):
            raise serializers.ValidationError(_("Rating must be in 0.5 increments."))

        return value

    def validate_comment(self, value):
        """
        Validate comment:
        - Minimum length for meaningful feedback
        - Maximum length to prevent abuse
        - Basic content validation
        """
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                _("Please provide at least 20 characters of feedback.")
            )

        if len(value) > 2000:
            raise serializers.ValidationError(
                _("Feedback comment cannot exceed 2000 characters.")
            )

        # Basic content validation
        if value.lower().count("http") > 2:
            raise serializers.ValidationError(
                _("Too many URLs in the feedback. Maximum 2 URLs allowed.")
            )

        if "<" in value and ">" in value:
            raise serializers.ValidationError(
                _("HTML tags are not allowed in feedback.")
            )

        return value.strip()

    def validate(self, data):
        """
        Cross-field validation:
        - Check update window for rating/recommendation changes
        """
        instance = self.instance
        if not instance.is_within_update_window:
            if "rating" in data or "is_recommended" in data:
                raise serializers.ValidationError(
                    {
                        "detail": _(
                            "Rating and recommendation can only be updated within 72 hours of creation."
                        )
                    }
                )

        return data
