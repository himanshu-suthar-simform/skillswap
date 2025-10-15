from rest_framework.throttling import UserRateThrottle


class HourlyUserRateThrottle(UserRateThrottle):
    """
    Throttle class to limit user requests per hour.
    Used for sensitive operations like creating skills.
    """

    rate = "10/hour"
    scope = "user_hourly"


class DailyUserRateThrottle(UserRateThrottle):
    """
    Throttle class to limit user requests per day.
    Prevents abuse and DoS attacks.
    """

    rate = "100/day"
    scope = "user_daily"


class ReviewRateThrottle(UserRateThrottle):
    """
    Combined throttle for feedback submission.
    Implements both hourly and daily limits to prevent review bombing.

    Limits:
    - 5 reviews per hour
    - 30 reviews per day

    This helps maintain feedback quality while preventing abuse.
    """

    rate = "5/hour"  # Default to hourly rate
    scope = "feedback_submission"
    cache_format = "throttle_%(scope)s_%(ident)s_%(period)s"

    def get_cache_key(self, request, view):
        """Generate a unique cache key based on the scope, user and period."""
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
            "period": "hourly" if self.rate == "5/hour" else "daily",
        }

    def allow_request(self, request, view):
        """Check both hourly and daily limits."""
        # Check hourly limit
        self.rate = "5/hour"
        self.duration = 3600  # 1 hour in seconds
        hourly_allowed = super().allow_request(request, view)

        if not hourly_allowed:
            return False

        # Check daily limit
        self.rate = "30/day"
        self.duration = 86400  # 24 hours in seconds
        daily_allowed = super().allow_request(request, view)

        return daily_allowed


class SkillCreationRateThrottle(UserRateThrottle):
    """
    Combined throttle for skill creation endpoints.
    Implements both hourly (10/hour) and daily (100/day) limits.
    """

    rate = "10/hour"  # Default to hourly rate
    scope = "skill_creation"
    cache_format = "throttle_%(scope)s_%(ident)s_%(period)s"

    def get_cache_key(self, request, view):
        """
        Generate a unique cache key based on the scope, user and period.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
            "period": "hourly" if self.rate == "10/hour" else "daily",
        }

    def allow_request(self, request, view):
        """
        Check both hourly and daily limits.
        """
        # Check hourly limit
        self.rate = "10/hour"
        self.duration = 3600  # 1 hour in seconds
        hourly_allowed = super().allow_request(request, view)

        if not hourly_allowed:
            return False

        # Check daily limit
        self.rate = "100/day"
        self.duration = 86400  # 24 hours in seconds
        daily_allowed = super().allow_request(request, view)

        return daily_allowed
