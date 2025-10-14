from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SkillCategoryViewSet
from .views import SkillViewSet

app_name = "skillhub"

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"categories", SkillCategoryViewSet, basename="category")
router.register(r"skills", SkillViewSet, basename="skill")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
