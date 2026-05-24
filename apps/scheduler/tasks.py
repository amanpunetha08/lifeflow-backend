from celery import shared_task
from .services import generate_daily_tasks, process_expired_tasks, update_daily_streaks


@shared_task
def task_generate_daily_tasks():
    generate_daily_tasks()


@shared_task
def task_process_expired_tasks():
    process_expired_tasks()


@shared_task
def task_update_daily_streaks():
    update_daily_streaks()
