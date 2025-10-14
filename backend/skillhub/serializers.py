from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Skill
from .models import SkillCategory


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
    total_teachers = serializers.IntegerField(read_only=True)

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
    total_teachers = serializers.IntegerField(read_only=True)

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
        if data.get("is_active", True) and not data["category"].is_active:
            raise serializers.ValidationError(
                {
                    "category": _(
                        "Cannot create/update an active skill in an inactive category."
                    )
                }
            )

        return data
