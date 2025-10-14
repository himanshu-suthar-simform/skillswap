from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Profile
from .models import User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model.
    Provides a user-friendly interface for managing user profiles with
    optimized queries and useful filters.
    """

    list_display = (
        "user_email",
        "user_full_name",
        "display_profile_picture",
        "location",
        "is_available",
        "created_at",
    )
    list_filter = (
        "is_available",
        "language_preference",
        "timezone",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "location",
        "phone_number",
    )
    readonly_fields = ("created_at", "updated_at")

    # Fieldsets for organized form layout
    fieldsets = (
        (_("User Information"), {"fields": ("user", "bio")}),
        (
            _("Profile Picture"),
            {
                "fields": ("profile_picture",),
                "description": _(
                    "Upload a profile picture (max 5MB). Supported formats: JPG, JPEG, PNG, GIF"
                ),
                "classes": ("collapse",),
            },
        ),
        (_("Contact Information"), {"fields": ("phone_number", "location")}),
        (
            _("Preferences"),
            {"fields": ("timezone", "language_preference", "is_available")},
        ),
        (
            _("Metadata"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_email(self, obj):
        """Get user's email."""
        return obj.user.email

    user_email.admin_order_field = "user__email"
    user_email.short_description = _("Email")

    def user_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_full_name.admin_order_field = "user__first_name"
    user_full_name.short_description = _("Full Name")

    def display_profile_picture(self, obj):
        """Display profile picture thumbnail in admin."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url,
            )
        return format_html('<span style="color: #999;">No Picture</span>')

    display_profile_picture.short_description = _("Profile Picture")

    # Optimize queries
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for User model.
    Extends Django's UserAdmin with additional fields and optimizations.
    """

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("role", "is_active", "is_staff", "created_at", "groups")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)

    # Fieldsets for organized form layout
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    # Fields for add form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    # Custom actions
    actions = ["activate_users", "deactivate_users"]

    def activate_users(self, request, queryset):
        """Bulk activate selected users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} users were successfully activated."))

    activate_users.short_description = _("Activate selected users")

    def deactivate_users(self, request, queryset):
        """Bulk deactivate selected users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} users were successfully deactivated."))

    deactivate_users.short_description = _("Deactivate selected users")

    # Optimize queries
    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("groups", "user_permissions")
        )
