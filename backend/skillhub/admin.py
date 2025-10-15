from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Skill
from .models import SkillCategory
from .models import SkillExchange
from .models import SkillFeedback
from .models import SkillMilestone
from .models import UserSkill


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for SkillCategory model.
    Provides category management with skill counts and status.
    """

    list_display = (
        "name",
        "description",
        "display_icon",
        "active_skills_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

    def display_icon(self, obj):
        """Display category icon with preview."""
        if obj.icon:
            return format_html(
                '<i class="{}" style="font-size: 20px;"></i> {}', obj.icon, obj.icon
            )
        return "-"

    display_icon.short_description = _("Icon")

    def active_skills_count(self, obj):
        """Display count of active skills in category."""
        return obj.get_active_skills_count()

    active_skills_count.short_description = _("Active Skills")


class SkillMilestoneInline(admin.TabularInline):
    """Inline admin for skill milestones."""

    model = SkillMilestone
    extra = 1
    fields = ("order", "title", "description", "estimated_hours")
    ordering = ("order",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin interface for the base Skill model.
    Provides management of skill definitions and categories.
    """

    list_display = (
        "name",
        "category",
        "total_teachers",
        "created_at",
    )
    list_filter = (
        "category",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "category__name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def total_teachers(self, obj):
        """Display number of teachers offering this skill."""
        count = obj.teachers.filter(is_active=True).count()
        return format_html('<span title="Active teachers">{}</span>', count)

    total_teachers.short_description = _("Active Teachers")


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSkill model.
    Provides comprehensive management of user's skill offerings with statistics and milestones.
    """

    inlines = [SkillMilestoneInline]

    list_display = (
        "skill",
        "user",
        "proficiency_level",
        "total_students",
        "display_rating",
        "display_success_rate",
        "is_active",
    )
    list_filter = (
        "is_active",
        "proficiency_level",
        "skill__category",
        "created_at",
    )
    search_fields = (
        "skill__name",
        "description",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "total_students",
    )

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "skill",
                    "user",
                    "proficiency_level",
                    "years_of_experience",
                )
            },
        ),
        (
            _("Credentials"),
            {"fields": ("certifications", "portfolio_links"), "classes": ("collapse",)},
        ),
        (
            _("Teaching Details"),
            {
                "fields": (
                    "prerequisites",
                    "learning_outcomes",
                    "teaching_methods",
                    "estimated_duration",
                    "duration_type",
                )
            },
        ),
        (
            _("Availability"),
            {"fields": ("is_active", "max_students", "available_time_slots")},
        ),
        (
            _("Statistics"),
            {
                "fields": ("total_students",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def display_rating(self, obj):
        """Display rating with stars."""
        rating = obj.average_rating
        if rating is None:
            return "No ratings"
        stars = "★" * int(rating)
        return f"{rating:.2f} {stars}"

    display_rating.short_description = _("Rating")

    def display_success_rate(self, obj):
        """Display success rate as percentage."""
        rate = obj.success_rate
        if rate is None:
            return "No transactions"
        return f"{rate:.2f}%"

    display_success_rate.short_description = _("Success Rate")

    def get_queryset(self, request):
        """Optimize queries with select_related and prefetch_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "skill", "skill__category")
            .prefetch_related("milestones")
        )


@admin.register(SkillFeedback)
class SkillFeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for SkillFeedback model.
    Manages student feedback and ratings for teacher's skills.
    """

    list_display = (
        "get_skill_name",
        "get_teacher_name",
        "get_learner_name",
        "display_rating",
        "is_recommended",
        "created_at",
    )
    list_filter = (
        "is_recommended",
        "exchange__user_skill__skill__category",
        "created_at",
        ("rating", admin.EmptyFieldListFilter),
    )
    search_fields = (
        "exchange__user_skill__skill__name",
        "exchange__user_skill__user__email",
        "exchange__user_skill__user__first_name",
        "exchange__user_skill__user__last_name",
        "exchange__learner__email",
        "exchange__learner__first_name",
        "exchange__learner__last_name",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")

    def get_skill_name(self, obj):
        """Display skill name."""
        return obj.user_skill.skill.name

    get_skill_name.short_description = _("Skill")
    get_skill_name.admin_order_field = "user_skill__skill__name"

    def get_teacher_name(self, obj):
        """Display teacher name."""
        user = obj.user_skill.user
        return user.get_full_name() or user.email

    get_teacher_name.short_description = _("Teacher")
    get_teacher_name.admin_order_field = "user_skill__user__first_name"

    def get_learner_name(self, obj):
        """Display learner name."""
        user = obj.exchange.learner
        return user.get_full_name() or user.email

    get_learner_name.short_description = _("Learner")
    get_learner_name.admin_order_field = "exchange__learner__first_name"

    def display_rating(self, obj):
        """Display rating with stars."""
        if obj.rating is None:
            return "No rating"
        stars = "★" * int(obj.rating)
        return f"{obj.rating:.2f} {stars}"

    display_rating.short_description = _("Rating")

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "exchange",
                "exchange__user_skill",
                "exchange__user_skill__user",
                "exchange__user_skill__skill",
                "exchange__learner",
            )
        )


@admin.register(SkillExchange)
class SkillExchangeAdmin(admin.ModelAdmin):
    """Admin interface for SkillExchange model."""

    list_display = (
        "get_skill_name",
        "get_teacher_name",
        "learner",
        "status",
        "proposed_duration",
        "created_at",
    )
    list_filter = ("status", "user_skill__skill__category", "created_at")
    search_fields = (
        "user_skill__skill__name",
        "user_skill__user__email",
        "user_skill__user__first_name",
        "user_skill__user__last_name",
        "learner__email",
        "learner__first_name",
        "learner__last_name",
        "learning_goals",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Exchange Details"),
            {"fields": ("user_skill", "learner", "status", "proposed_duration")},
        ),
        (
            _("Learning Information"),
            {
                "fields": ("learning_goals", "availability"),
            },
        ),
        (_("Additional Information"), {"fields": ("notes",), "classes": ("collapse",)}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_skill_name(self, obj):
        """Display skill name."""
        return obj.user_skill.skill.name

    get_skill_name.short_description = _("Skill")
    get_skill_name.admin_order_field = "user_skill__skill__name"

    def get_teacher_name(self, obj):
        """Display teacher name."""
        user = obj.user_skill.user
        return user.get_full_name() or user.email

    get_teacher_name.short_description = _("Teacher")
    get_teacher_name.admin_order_field = "user_skill__user__first_name"

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user_skill", "user_skill__user", "user_skill__skill", "learner"
            )
        )
