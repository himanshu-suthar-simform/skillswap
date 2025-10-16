import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"skillswap.settings.{DJANGO_ENV}")

app = Celery("skillswap")

# Read config from Django settings, using CELERY namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered apps
app.autodiscover_tasks()

# Manually defining periodic tasks.
# We can create the tasks dynamically using custom command `python manage.py create_periodic_tasks` if needed.
app.conf.beat_schedule = {
    "cleanup-inactive-skills": {
        "task": "skillhub.tasks.skill_cleanup.remove_inactive_categories_and_skills",
        "schedule": crontab(hour=0, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
