from accounts.models import User
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class SkillCategory(models.Model):
    """
    Categories for organizing skills (e.g., Programming, Languages, Music, etc.).
    Helps in better organization and discovery of skills.
    """

    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("Category name (e.g., Programming, Music, Languages)"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Brief description of this skill category"),
    )
    icon = models.CharField(
        _("icon class"),
        max_length=50,
        blank=True,
        help_text=_("CSS class for category icon (e.g., 'fa-code' for programming)"),
    )
    is_active = models.BooleanField(
        _("active status"),
        default=True,
        help_text=_("Whether this category is active and visible"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("skill category")
        verbose_name_plural = _("skill categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_active_skills_count(self):
        """Get count of active skills in this category."""
        return self.skills.filter(is_active=True).count()


class Skill(models.Model):
    """
    Base model for skills that can be taught.
    This represents the fundamental skill itself, independent of who teaches it.
    """

    name = models.CharField(
        _("skill name"),
        max_length=200,
        unique=True,
        help_text=_(
            "Name of the skill (e.g., 'Python Programming', 'Spanish Language')"
        ),
    )
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.PROTECT,
        related_name="skills",
        verbose_name=_("category"),
    )
    description = models.TextField(
        _("description"), help_text=_("General description of what this skill entails")
    )

    is_active = models.BooleanField(
        _("active status"),
        default=True,
        help_text=_("Whether this skill is currently available for teaching"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("skill")
        verbose_name_plural = _("skills")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name

    @property
    def total_teachers(self):
        """Get the total number of users teaching this skill."""
        return self.teachers.filter(is_active=True).count()


class UserSkill(models.Model):
    """
    Model representing a user's specific skill offering.
    This contains all the teaching-specific information for a user's skill.
    """

    class ProficiencyLevel(models.TextChoices):
        BEGINNER = "BEGINNER", _("Beginner")
        INTERMEDIATE = "INTERMEDIATE", _("Intermediate")
        ADVANCED = "ADVANCED", _("Advanced")
        EXPERT = "EXPERT", _("Expert")

    class DurationType(models.TextChoices):
        HOURS = "HOURS", _("Hours")
        DAYS = "DAYS", _("Days")
        WEEKS = "WEEKS", _("Weeks")
        MONTHS = "MONTHS", _("Months")

    # Basic Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teaching_skills",
        verbose_name=_("teacher"),
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="teachers",
        verbose_name=_("skill"),
    )

    # Teaching Qualifications
    proficiency_level = models.CharField(
        _("proficiency level"),
        max_length=20,
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.INTERMEDIATE,
    )
    years_of_experience = models.PositiveSmallIntegerField(
        _("years of experience"),
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text=_("Years of experience in this skill"),
    )
    certifications = models.TextField(
        _("certifications"),
        blank=True,
        help_text=_("List any relevant certifications or qualifications"),
    )
    portfolio_links = models.TextField(
        _("portfolio links"),
        blank=True,
        help_text=_("Links to portfolios, projects, or work samples"),
    )

    # Teaching Details
    prerequisites = models.TextField(
        _("prerequisites"),
        blank=True,
        help_text=_("Required prerequisites for learning this skill"),
    )
    learning_outcomes = models.TextField(
        _("learning outcomes"), help_text=_("What students will learn/achieve")
    )
    teaching_methods = models.TextField(
        _("teaching methods"), help_text=_("Your approach to teaching this skill")
    )
    estimated_duration = models.PositiveSmallIntegerField(
        _("estimated duration"),
        validators=[MinValueValidator(1)],
        help_text=_("Estimated time to learn basics"),
    )
    duration_type = models.CharField(
        _("duration type"),
        max_length=10,
        choices=DurationType.choices,
        default=DurationType.HOURS,
    )

    # Availability & Status
    is_active = models.BooleanField(
        _("active status"),
        default=True,
        help_text=_("Whether this skill is currently available for teaching"),
    )
    max_students = models.PositiveSmallIntegerField(
        _("maximum students"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text=_("Maximum number of simultaneous students"),
    )
    available_time_slots = models.TextField(
        _("available time slots"),
        blank=True,
        help_text=_("Describe your available time slots for teaching"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user skill")
        verbose_name_plural = _("user skills")
        ordering = ["-created_at"]
        unique_together = [["user", "skill"]]  # A user can teach a skill only once
        indexes = [
            models.Index(fields=["user", "skill", "is_active"]),
            models.Index(fields=["proficiency_level", "is_active"]),
        ]

    def __str__(self):
        return f"{self.skill.name} by {self.user.get_full_name() or self.user.email}"

    def get_absolute_url(self):
        """Get the absolute URL for this user's skill offering."""
        from django.urls import reverse

        return reverse("skillhub:user-skill-detail", kwargs={"pk": self.pk})

    @property
    def total_students(self):
        """Get total number of students who have taken this skill from this teacher."""
        return self.exchanges.count()

    @property
    def average_rating(self):
        """Calculate average rating from feedback."""
        avg = (
            self.feedback_received.aggregate(avg_rating=models.Avg("rating"))[
                "avg_rating"
            ]
            or 0.00
        )
        return round(avg, 2)

    @property
    def success_rate(self):
        """Calculate success rate based on completed exchanges."""
        total = self.total_students
        if total == 0:
            return 0.00
        successful = self.exchanges.filter(status="COMPLETED").count()
        return round((successful / total) * 100, 2)

    @property
    def total_feedback_count(self):
        """Get total number of feedback received."""
        return self.feedback_received.count()


class SkillMilestone(models.Model):
    """
    Milestones or checkpoints in learning a skill.
    Helps track progress and set clear expectations.
    """

    user_skill = models.ForeignKey(
        UserSkill,
        on_delete=models.CASCADE,
        related_name="milestones",
        verbose_name=_("user skill"),
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"))
    order = models.PositiveSmallIntegerField(
        _("order"), help_text=_("Order of this milestone in the learning path")
    )
    estimated_hours = models.PositiveSmallIntegerField(
        _("estimated hours"),
        validators=[MinValueValidator(1)],
        help_text=_("Estimated hours to complete this milestone"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("skill milestone")
        verbose_name_plural = _("skill milestones")
        ordering = ["user_skill", "order"]
        unique_together = ["user_skill", "order"]

    def __str__(self):
        return f"{self.user_skill} - Milestone {self.order}: {self.title}"


class SkillFeedback(models.Model):
    """
    Feedback and ratings from students for a specific teacher's skill.
    Helps maintain quality and provide social proof.
    """

    user_skill = models.ForeignKey(
        UserSkill,
        on_delete=models.CASCADE,
        related_name="feedback_received",
        verbose_name=_("user skill"),
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedback_given",
        verbose_name=_("student"),
    )
    rating = models.DecimalField(
        _("rating"),
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        help_text=_("Rating from 0 to 5"),
        null=True,
        blank=True,
    )
    comment = models.TextField(_("comment"))
    is_recommended = models.BooleanField(
        _("recommended"),
        default=True,
        help_text=_("Would you recommend this skill/teacher to others?"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("skill feedback")
        verbose_name_plural = _("skill feedback")
        ordering = ["-created_at"]
        unique_together = ["user_skill", "student"]  # Changed from skill to user_skill
        indexes = [
            models.Index(
                fields=["user_skill", "-created_at"]
            ),  # Changed from skill to user_skill
            models.Index(fields=["-rating", "-created_at"]),
        ]

    def __str__(self):
        return f"Feedback for {self.user_skill} by {self.student.get_full_name() or self.student.email}"

    def save(self, *args, **kwargs):
        """Override save to perform any future validations."""
        super().save(*args, **kwargs)


class SkillExchange(models.Model):
    """
    Model to track skill exchanges between users.
    Records the agreement between a teacher and student for skill learning.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        ACCEPTED = "ACCEPTED", _("Accepted")
        IN_PROGRESS = "IN_PROGRESS", _("In Progress")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    user_skill = models.ForeignKey(
        UserSkill,
        on_delete=models.PROTECT,
        related_name="exchanges",
        verbose_name=_("teacher skill"),
        help_text=_("The skill being taught"),
    )
    learner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="learning_exchanges",
        verbose_name=_("learner"),
        help_text=_("User learning the skill"),
    )
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.PENDING
    )
    learning_goals = models.TextField(
        _("learning goals"), help_text=_("What the learner wants to achieve")
    )
    availability = models.TextField(
        _("availability"), help_text=_("Preferred time slots for learning sessions")
    )
    proposed_duration = models.PositiveSmallIntegerField(
        _("proposed duration"),
        validators=[MinValueValidator(1)],
        help_text=_("Estimated number of hours needed for learning"),
    )
    notes = models.TextField(
        _("notes"), blank=True, help_text=_("Additional notes or requirements")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("skill exchange")
        verbose_name_plural = _("skill exchanges")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_skill", "status", "-created_at"]),
            models.Index(fields=["learner", "status", "-created_at"]),
        ]
        permissions = [
            ("can_accept_exchange", "Can accept skill exchange"),
            ("can_mark_completed", "Can mark exchange as completed"),
        ]

    def __str__(self):
        return f"{self.user_skill} - {self.learner.get_full_name() or self.learner.email} ({self.status})"

    def get_teacher(self):
        """Get the teacher for this exchange."""
        return self.user_skill.user

    @property
    def teacher(self):
        """Alias for get_teacher for consistency."""
        return self.get_teacher()
