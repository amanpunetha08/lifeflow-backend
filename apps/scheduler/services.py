from django.utils import timezone
from datetime import timedelta
from apps.tasks.models import Task
from apps.gamification.models import XPLog, StreakRecord
from .models import RecurringRule, ScheduledEvent


def generate_daily_tasks():
    """Generate today's recurring task instances for all active rules."""
    today = timezone.now().date()
    day_of_week = today.weekday()

    rules = RecurringRule.objects.filter(
        is_active=True,
        start_date__lte=today,
    ).exclude(last_generated=today).select_related('task_template', 'user')

    for rule in rules:
        if rule.end_date and rule.end_date < today:
            rule.is_active = False
            rule.save()
            continue

        # Check if today matches the recurrence pattern
        template = rule.task_template
        should_generate = False

        if template.recurrence_type == Task.RecurrenceType.DAILY:
            should_generate = True
        elif template.recurrence_type == Task.RecurrenceType.WEEKDAYS:
            should_generate = day_of_week < 5
        elif template.recurrence_type == Task.RecurrenceType.WEEKLY:
            should_generate = day_of_week in rule.days_of_week
        elif template.recurrence_type == Task.RecurrenceType.MONTHLY:
            should_generate = today.day == rule.start_date.day

        if should_generate:
            # Create today's instance
            instance = Task.objects.create(
                user=rule.user,
                title=template.title,
                description=template.description,
                priority=template.priority,
                status=Task.Status.TODO,
                tags=template.tags,
                category=template.category,
                color=template.color,
                icon=template.icon,
                start_time=timezone.make_aware(
                    timezone.datetime.combine(today, template.start_time.time())
                ) if template.start_time else None,
                end_time=timezone.make_aware(
                    timezone.datetime.combine(today, template.end_time.time())
                ) if template.end_time else None,
                estimated_duration=template.estimated_duration,
                recurrence_type=template.recurrence_type,
                is_recurring=True,
                parent_task=template,
                xp_reward=template.xp_reward,
                penalty_points=template.penalty_points,
                original_date=today,
            )

            ScheduledEvent.objects.create(
                user=rule.user, task=instance, event_type=ScheduledEvent.EventType.GENERATED
            )

        rule.last_generated = today
        rule.save()


def process_expired_tasks():
    """Process tasks that have passed the user's day_end_time."""
    now = timezone.now()
    from django.contrib.auth import get_user_model
    User = get_user_model()

    for user in User.objects.all():
        # Check if current time is past user's day end
        user_day_end = timezone.make_aware(
            timezone.datetime.combine(now.date(), user.day_end_time)
        )
        if now < user_day_end:
            continue

        # Get all pending tasks for this user today
        pending_tasks = Task.objects.filter(
            user=user,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
            start_time__date__lte=now.date(),
        )

        for task in pending_tasks:
            if task.is_recurring and not task.parent_task:
                # Daily recurring: mark missed, apply penalty, don't roll over
                task.status = Task.Status.MISSED
                task.save()

                user.discipline_score = max(0, user.discipline_score - 2)
                user.chaos_meter = min(100, user.chaos_meter + 3)
                user.save()

                XPLog.objects.create(
                    user=user, amount=-task.penalty_points,
                    reason=f'Missed recurring task: {task.title}', task=task
                )
                ScheduledEvent.objects.create(
                    user=user, task=task, event_type=ScheduledEvent.EventType.MISSED
                )
                ScheduledEvent.objects.create(
                    user=user, task=task, event_type=ScheduledEvent.EventType.PENALTY_APPLIED,
                    details={'penalty': task.penalty_points}
                )
            else:
                # Non-recurring / timeframe subtask: roll over to tomorrow
                tomorrow = (now + timedelta(days=1)).date()
                tomorrow_start = timezone.make_aware(
                    timezone.datetime.combine(tomorrow, user.day_start_time)
                )
                tomorrow_end = timezone.make_aware(
                    timezone.datetime.combine(tomorrow, user.day_end_time)
                )

                task.status = Task.Status.TODO
                task.is_rolled_over = True
                task.rollover_count += 1
                task.start_time = tomorrow_start
                task.end_time = tomorrow_end
                task.save()

                user.discipline_score = max(0, user.discipline_score - 1)
                user.chaos_meter = min(100, user.chaos_meter + 2)
                user.save()

                XPLog.objects.create(
                    user=user, amount=-task.penalty_points,
                    reason=f'Missed task (moved to next day): {task.title}', task=task
                )
                ScheduledEvent.objects.create(
                    user=user, task=task, event_type=ScheduledEvent.EventType.ROLLED_OVER
                )


def update_daily_streaks():
    """Update streak records at end of day."""
    today = timezone.now().date()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    for user in User.objects.all():
        today_tasks = Task.objects.filter(user=user, start_time__date=today)
        total = today_tasks.count()
        completed = today_tasks.filter(status=Task.Status.COMPLETED).count()

        if total == 0:
            continue

        is_perfect = completed == total
        record, _ = StreakRecord.objects.update_or_create(
            user=user, date=today,
            defaults={
                'tasks_completed': completed,
                'tasks_total': total,
                'is_perfect_day': is_perfect,
            }
        )

        if completed > 0:
            user.streak_count += 1
            user.longest_streak = max(user.longest_streak, user.streak_count)
            if is_perfect:
                user.discipline_score = min(100, user.discipline_score + 2)
                user.chaos_meter = max(0, user.chaos_meter - 5)
        else:
            user.streak_count = 0

        user.save()
