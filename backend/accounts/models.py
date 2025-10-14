from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser to add role-based functionality.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        USER = "USER", _("Learner/Teacher")

    # Basic fields
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=False)  # Requires admin approval
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Required for using email as the login field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    User Profile model containing additional user information.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(_("biography"), max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/%Y/%m/",
        null=True,
        blank=True,
        help_text=_("Profile picture (max 5MB, must be an image)"),
    )
    phone_number = models.CharField(
        max_length=15, blank=True, help_text=_("Contact phone number")
    )
    location = models.CharField(
        max_length=100, blank=True, help_text=_("City, Country")
    )
    timezone = models.CharField(
        max_length=50, default="UTC", help_text=_("User's timezone for scheduling")
    )
    language_preference = models.CharField(
        max_length=10, default="en", help_text=_("Preferred language for communication")
    )
    is_available = models.BooleanField(
        default=True, help_text=_("User availability status")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}'s profile"
