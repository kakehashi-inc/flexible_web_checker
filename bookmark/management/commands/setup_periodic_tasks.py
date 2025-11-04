from django.core.management.base import BaseCommand
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = 'Initialize and update periodic tasks'

    def handle(self, *args, **options):
        self.stdout.write('Setting up periodic tasks...')

        # Create crontab schedule based on UPDATE_CHECK_SCHEDULE
        schedule_str = settings.UPDATE_CHECK_SCHEDULE
        parts = schedule_str.split()

        if len(parts) != 5:
            self.stdout.write(self.style.ERROR(
                f'UPDATE_CHECK_SCHEDULE format is incorrect: {schedule_str}\n'
                'Correct format: minute hour day_of_month month_of_year day_of_week\n'
                'Example: 0 * * * * (every hour at minute 0)'
            ))
            return

        minute, hour, day_of_month, month_of_year, day_of_week = parts

        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new schedule: {schedule}'))
        else:
            self.stdout.write(f'Using existing schedule: {schedule}')

        # Create/update periodic URL check task
        task, created = PeriodicTask.objects.update_or_create(
            name='Periodic URL Update Check',
            defaults={
                'task': 'bookmark.tasks.url_check.check_url_updates',
                'crontab': schedule,
                'enabled': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created periodic URL update check task'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated periodic URL update check task'))

        self.stdout.write(self.style.SUCCESS(f'Task name: {task.name}'))
        self.stdout.write(self.style.SUCCESS(f'Schedule: {task.crontab}'))
        self.stdout.write(self.style.SUCCESS(f'Enabled: {task.enabled}'))
