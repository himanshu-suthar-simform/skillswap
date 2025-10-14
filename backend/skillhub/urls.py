from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SkillCategoryViewSet
from .views import SkillExchangeViewSet
from .views import SkillViewSet
from .views import UserSkillViewSet

app_name = "skillhub"

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"categories", SkillCategoryViewSet, basename="category")
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"teaching-skills", UserSkillViewSet, basename="teaching-skill")

# Register the exchange viewset
router.register(r"exchanges", SkillExchangeViewSet, basename="exchange")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
