import os

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile
from .models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for User model.
    Used for nested representations where only basic user info is needed.
    """

    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "profile_picture_url",
            "is_active",
        ]
        read_only_fields = fields

    @extend_schema_field(str)
    def get_full_name(self, obj):
        """Get user's full name or username if name not set."""
        return obj.get_full_name() or obj.username

    @extend_schema_field({"type": "string", "format": "uri", "nullable": True})
    def get_profile_picture_url(self, obj):
        """Get URL of user's profile picture if it exists."""
        try:
            if obj.profile and obj.profile.profile_picture:
                return obj.profile.profile_picture.url
        except Profile.DoesNotExist:
            pass
        return None


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    This serializer handles the user profile information that complements
    the main User model. It's designed to work both independently and as
    a nested serializer within UserSerializer.
    """

    # Add profile picture URL for read operations
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "bio",
            "profile_picture",
            "profile_picture_url",
            "phone_number",
            "location",
            "timezone",
            "language_preference",
            "is_available",
        ]
        extra_kwargs = {
            "phone_number": {"required": False},
            "location": {"required": False},
            "timezone": {"required": False},
            "language_preference": {"required": False},
            "is_available": {"required": False},
            "profile_picture": {"write_only": True},
        }

    def get_profile_picture_url(self, obj):
        """
        Get the complete URL for the profile picture.

        Args:
            obj: Profile instance

        Returns:
            str: Complete URL to the profile picture if it exists, None otherwise
        """
        if obj.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def validate_profile_picture(self, value):
        """
        Validate the profile picture upload.

        Validates:
        1. File size (max 5MB)
        2. File type (must be image)
        3. Image dimensions (min 100x100, max 4000x4000)

        Args:
            value: The uploaded file

        Returns:
            File: The validated file

        Raises:
            serializers.ValidationError: If validation fails
        """
        if not value:
            return value

        # Check file size (5MB limit)
        if value.size > settings.MAX_FILE_UPLOAD_SIZE:
            raise serializers.ValidationError(
                "Profile picture size should not exceed 5MB."
            )

        # Check file type
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG and GIF files are allowed."
            )

        # Check image dimensions
        width, height = get_image_dimensions(value)
        if not width or not height:
            raise serializers.ValidationError("Uploaded file is not a valid image.")

        if width < 100 or height < 100:
            raise serializers.ValidationError(
                "Image dimensions must be at least 100x100 pixels."
            )

        if width > 4000 or height > 4000:
            raise serializers.ValidationError(
                "Image dimensions must not exceed 4000x4000 pixels."
            )

        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer handles the creation of both User and Profile models
    through a single API endpoint. It includes custom validation for the
    password field and ensures all required fields are properly validated.

    The serializer automatically:
    1. Creates a user with encrypted password
    2. Creates an associated profile
    3. Sets the default role as USER
    4. Validates password strength
    5. Ensures email uniqueness
    """

    # Add write-only password confirmation field
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Confirm password (must match password field)",
    )

    # Nested profile serializer for creating profile along with user
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "profile",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "help_text": "Password must meet system requirements",
            },
            "id": {"read_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_email(self, value):
        """
        Validate email uniqueness and format.

        Args:
            value: The email to validate

        Returns:
            str: The validated email

        Raises:
            serializers.ValidationError: If email is invalid or already exists
        """
        # Email is automatically validated by EmailField
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password strength using Django's password validators.

        Args:
            value: The password to validate

        Returns:
            str: The validated password

        Raises:
            serializers.ValidationError: If password doesn't meet requirements
        """
        try:
            # Use Django's built-in password validation
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        """
        Validate the entire data set.

        Ensures:
        1. Password and password_confirm match
        2. Required fields are present

        Args:
            data: The data to validate

        Returns:
            dict: The validated data

        Raises:
            serializers.ValidationError: If validation fails
        """
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation doesn't match password."}
            )
        return data

    def create(self, validated_data):
        """
        Create a new user and associated profile.

        This method:
        1. Removes password_confirm from validated_data
        2. Extracts profile data if present
        3. Creates the user with a hashed password
        4. Creates the associated profile

        Args:
            validated_data: The validated data from which to create the user

        Returns:
            User: The newly created user instance
        """
        # Remove password confirmation field
        validated_data.pop("password_confirm", None)

        # Extract profile data
        profile_data = validated_data.pop("profile", {})

        # Set role as USER
        validated_data["role"] = User.Role.USER

        # Create user instance but don't save yet
        password = validated_data.pop("password")
        user = User(**validated_data)

        # Set and hash password
        user.set_password(password)
        user.save()

        # Create profile
        Profile.objects.create(user=user, **profile_data)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom Token Obtain Pair Serializer that includes additional user information
    in the response along with the access and refresh tokens.
    """

    def validate(self, attrs):
        # Get the default token data (access and refresh tokens)
        data = super().validate(attrs)

        # Add custom claims to both access and refresh tokens
        self.add_user_context_to_token(data)

        return data

    def add_user_context_to_token(self, data):
        """
        Add user context information to token response.

        Args:
            data (dict): The token data dictionary to update
        """
        user = self.user
        # Add basic user information
        data.update(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                }
            }
        )

        # Add profile information if it exists
        if hasattr(user, "profile"):
            profile = user.profile
            data["user"].update(
                {
                    "profile": {
                        "bio": profile.bio,
                        "location": profile.location,
                        "timezone": profile.timezone,
                        "language_preference": profile.language_preference,
                        "is_available": profile.is_available,
                    }
                }
            )

            # Add profile picture URL if it exists
            if profile.profile_picture:
                request = self.context.get("request")
                if request:
                    data["user"]["profile"]["profile_picture_url"] = (
                        request.build_absolute_uri(profile.profile_picture.url)
                    )


class UserDetailSerializer(UserBasicSerializer):
    """
    Detailed serializer for User model.
    Extends UserBasicSerializer to include additional user information.
    Used for retrieving user details and profile information.
    """

    profile = ProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "profile",
            "date_joined",
            "last_login",
            "is_active",
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Allows updating both User and Profile model fields in a single request.
    """

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "profile",
        ]

    def validate_first_name(self, value):
        """Validate first_name."""
        if not value.strip():
            raise serializers.ValidationError(_("First name cannot be empty."))
        if len(value) > 150:
            raise serializers.ValidationError(
                _("First name cannot exceed 150 characters.")
            )
        return value.strip()

    def validate_last_name(self, value):
        """Validate last_name."""
        if not value.strip():
            raise serializers.ValidationError(_("Last name cannot be empty."))
        if len(value) > 150:
            raise serializers.ValidationError(
                _("Last name cannot exceed 150 characters.")
            )
        return value.strip()

    def update(self, instance, validated_data):
        """
        Update user and profile information.

        Args:
            instance: User instance to update
            validated_data: Validated data containing user and profile fields

        Returns:
            User: Updated user instance
        """
        # Extract profile data
        profile_data = validated_data.pop("profile", {})

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile
        if profile_data and hasattr(instance, "profile"):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class UserListSerializer(UserBasicSerializer):
    """
    Serializer for listing users.
    Extends UserBasicSerializer to include minimal additional information.
    Used for user listing and search results.
    """

    profile = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "profile",
            "profile_picture_url",
            "date_joined",
            "is_active",
        ]
        read_only_fields = fields

    def get_profile(self, obj):
        """
        Get minimal profile information for list view.

        Args:
            obj: User instance

        Returns:
            dict: Basic profile information
        """
        try:
            return {
                "location": obj.profile.location,
                "is_available": obj.profile.is_available,
            }
        except Profile.DoesNotExist:
            return None
