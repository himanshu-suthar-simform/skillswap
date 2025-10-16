# skillhub/management/commands/create_periodic_task.py
import logging

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create a periodic Celery task with a specified schedule and task path"

    def add_arguments(self, parser):
        parser.add_argument(
            "--task-path",
            type=str,
            required=True,
            help="Full Celery task path (e.g., skillhub.tasks.cleanup_inactive_skills_and_categories)",
        )
        parser.add_argument(
            "--task-name",
            type=str,
            default="Periodic Celery Task",
            help="Name of the periodic task",
        )
        parser.add_argument(
            "--hour",
            type=int,
            default=0,
            help="Hour to run the task (0-23, default 0 for 12AM)",
        )
        parser.add_argument(
            "--minute",
            type=int,
            default=0,
            help="Minute to run the task (0-59, default 0)",
        )

    def handle(self, *args, **options):
        task_path = options["task_path"]
        task_name = options["task_name"]
        hour = options["hour"]
        minute = options["minute"]

        # 1️⃣ Create or get crontab schedule
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=str(minute),
            hour=str(hour),
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )
        if created:
            logger.info(f"Created new CrontabSchedule: {hour}:{minute}")
        else:
            logger.info(f"Using existing CrontabSchedule: {hour}:{minute}")

        # 2️⃣ Create or get the periodic task
        task, task_created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name=task_name,
            task=task_path,
            defaults={"enabled": True},
        )

        if task_created:
            logger.info(f"Created periodic task: {task_name} -> {task_path}")
        else:
            logger.info(f"Periodic task already exists: {task_name} -> {task_path}")

        self.stdout.write(self.style.SUCCESS(f"Task setup completed: {task_name}"))
