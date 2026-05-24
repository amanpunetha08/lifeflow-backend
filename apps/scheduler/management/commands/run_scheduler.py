from django.core.management.base import BaseCommand
from apps.scheduler.services import process_expired_tasks, generate_daily_tasks, update_daily_streaks


class Command(BaseCommand):
    help = 'Process expired tasks, generate daily tasks, and update streaks'

    def handle(self, *args, **options):
        process_expired_tasks()
        generate_daily_tasks()
        update_daily_streaks()
        self.stdout.write(self.style.SUCCESS('Scheduler tasks completed'))
