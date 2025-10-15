from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import BasePermission


class AdminOrReadOnly(BasePermission):
    """
    Custom permission to allow:
    - Admin users, staff users, and superusers to perform all operations
    - Regular authenticated users to only retrieve or create
    """

    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow read and create operations for all authenticated users
        if request.method in SAFE_METHODS or request.method == "POST":
            return True

        # Allow update and delete for admin users, staff users, and superusers
        return bool(
            request.user.role == "ADMIN"
            or request.user.is_staff
            or request.user.is_superuser
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission that allows:
    - Read access to authenticated users
    - Write access only to the owner of the object
    - Full access to admin users

    This is used for resources like feedback where:
    - Anyone can read public feedback
    - Only the feedback creator can edit their feedback
    - Admins can moderate all feedback
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS for any authenticated user
        if request.method in SAFE_METHODS:
            return True

        # Allow admins full access
        if (
            request.user.role == "ADMIN"
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return True

        # For feedback objects
        if hasattr(obj, "student"):
            return obj.student == request.user

        # For other objects, check user attribute
        return obj.user == request.user


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission for UserSkill objects that allows:
    - Admin/staff/superusers to perform any operation
    - Regular users to perform operations only on their own skills
    - Anyone to read active skills (list/retrieve)
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow admins full access
        if (
            request.user.role == "ADMIN"
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return True

        # Allow read operations for all authenticated users
        if request.method in SAFE_METHODS:
            return True

        # For create operations, always allow authenticated users
        if request.method == "POST":
            return True

        # For other methods, check object-level permissions
        return True

    def has_object_permission(self, request, view, obj):
        # Allow admins full access
        if (
            request.user.role == "ADMIN"
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return True

        # Allow read operations for active skills
        if request.method in SAFE_METHODS:
            return obj.is_active or obj.user == request.user

        # For other operations, check if user is the owner
        return obj.user == request.user
