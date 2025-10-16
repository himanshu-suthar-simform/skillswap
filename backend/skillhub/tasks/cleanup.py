# skillhub/tasks/cleanup.py
import logging

from celery import shared_task
from django.db import transaction
from django.db.models import Count
from skillhub.models import Skill
from skillhub.models import SkillCategory

# Configure logger for this module
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_inactive_skills_and_categories(self):
    """
    Celery task to remove inactive SkillCategories and Skills that are
    not linked to any active UserSkill or other dependent objects.

    Safety measures:
    1. Only deletes SkillCategory if it has no Skills.
    2. Only deletes Skill if it has no UserSkill (teachers) associated.
    3. Uses database transactions for atomic operations.
    4. Logs all deletions for monitoring and auditing.

    Returns:
        dict: Summary of deletions {'categories_deleted': X, 'skills_deleted': Y}
    """

    try:
        with transaction.atomic():
            # --- Delete inactive SkillCategories with no skills ---
            categories_to_delete = SkillCategory.objects.annotate(
                skill_count=Count("skills")
            ).filter(is_active=False, skill_count=0)
            categories_count = categories_to_delete.count()
            if categories_count > 0:
                logger.info(
                    f"Deleting {categories_count} inactive skill categories with no linked skills."
                )
                categories_to_delete.delete()
            else:
                logger.info("No inactive skill categories found for deletion.")

            # --- Delete inactive Skills with no active UserSkill ---
            skills_to_delete = Skill.objects.annotate(
                user_skill_count=Count("teachers")
            ).filter(is_active=False, user_skill_count=0)
            skills_count = skills_to_delete.count()
            if skills_count > 0:
                logger.info(
                    f"Deleting {skills_count} inactive skills with no linked teachers."
                )
                skills_to_delete.delete()
            else:
                logger.info("No inactive skills found for deletion.")

        # Return summary
        return {"categories_deleted": categories_count, "skills_deleted": skills_count}

    except Exception as exc:
        logger.exception(
            "Error occurred while cleaning up inactive skills and categories."
        )
        raise self.retry(exc=exc)
