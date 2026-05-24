from django.utils import timezone
from datetime import timedelta
import zoneinfo
from apps.tasks.models import Task
from apps.gamification.models import XPLog, StreakRecord
from .models import RecurringRule, ScheduledEvent

IST = zoneinfo.ZoneInfo('Asia/Kolkata')

# Demerit points by priority
DEMERIT_POINTS = {
    'high': {'xp': -10, 'discipline': -3, 'chaos': 5},
    'medium': {'xp': -5, 'discipline': -2, 'chaos': 3},
    'low': {'xp': -2, 'discipline': -1, 'chaos': 1},
    'urgent': {'xp': -10, 'discipline': -3, 'chaos': 5},
}


def _today():
    """Get today's date in IST."""
    return timezone.now().astimezone(IST).date()


def process_expired_tasks():
    """
    Daily processing script. Safe to call on every refresh.
    Uses user.last_processed_date to ensure it only runs once per day.

    Logic:
    1. Skip if already processed today
    2. Get all yesterday's tasks (daily routines + pending tasks)
    3. Calculate demerit points based on priority (high > medium > low)
    4. Daily routine not completed = highest demerit (they're high priority)
    5. Create fresh daily tasks for today
    6. Mark last_processed_date = today
    """
    now = timezone.now()
    today = _today()
    yesterday = today - timedelta(days=1)

    from django.contrib.auth import get_user_model
    User = get_user_model()

    for user in User.objects.all():
        # Already processed today? Skip.
        if user.last_processed_date == today:
            continue

        # Check if it's past user's day_end_time OR it's a new day
        user_day_end = timezone.make_aware(
            timezone.datetime.combine(today, user.day_end_time)
        )

        # If it's still today and before day_end, only process if last_processed < yesterday
        # (meaning we missed processing yesterday entirely)
        if now < user_day_end and user.last_processed_date == yesterday:
            continue

        # --- STEP 1: Get all tasks from previous days that are still pending ---
        old_pending_tasks = Task.objects.filter(
            user=user,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
            start_time__date__lt=today,
        )

        # --- STEP 2: Get daily routine tasks from yesterday (completed or not) ---
        yesterday_daily = Task.objects.filter(
            user=user,
            task_type='daily',
            is_recurring=True,
            start_time__date__lt=today,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        )

        streak_broken = False

        # --- STEP 3: Process incomplete daily routine tasks (HIGH demerit) ---
        for task in yesterday_daily:
            demerit = DEMERIT_POINTS.get(task.priority, DEMERIT_POINTS['high'])

            task.status = Task.Status.MISSED
            task.save()

            user.discipline_score = max(0, user.discipline_score + demerit['discipline'])
            user.chaos_meter = min(100, user.chaos_meter + demerit['chaos'])
            streak_broken = True

            XPLog.objects.create(
                user=user, amount=demerit['xp'],
                reason=f'Missed daily task: {task.title} (priority: {task.priority})', task=task
            )

        # --- STEP 4: Process other pending tasks (rollover as penalty tasks for today) ---
        other_pending = old_pending_tasks.exclude(
            id__in=yesterday_daily.values_list('id', flat=True)
        )

        for task in other_pending:
            demerit = DEMERIT_POINTS.get(task.priority, DEMERIT_POINTS['medium'])

            # Mark original as missed
            task.status = Task.Status.MISSED
            task.save()

            # Create penalty rollover task for today
            Task.objects.create(
                user=user,
                title=f"[Pending] {task.title}",
                description=task.description,
                task_type=task.task_type,
                priority=task.priority,
                status=Task.Status.TODO,
                tags=task.tags,
                category=task.category,
                color='#ef4444',  # Red color for penalty tasks
                is_recurring=False,
                xp_reward=task.xp_reward,
                penalty_points=task.penalty_points,
                is_rolled_over=True,
                rollover_count=task.rollover_count + 1,
                original_date=task.original_date or (task.start_time.date() if task.start_time else yesterday),
                parent_task=task.parent_task,
                start_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_start_time)
                ),
                end_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_end_time)
                ),
            )

            user.discipline_score = max(0, user.discipline_score + demerit['discipline'])
            user.chaos_meter = min(100, user.chaos_meter + demerit['chaos'])

            XPLog.objects.create(
                user=user, amount=demerit['xp'],
                reason=f'Pending task rolled over: {task.title} (priority: {task.priority})', task=task
            )

        # --- STEP 5: Update streak ---
        if streak_broken:
            user.streak_count = 0
        else:
            # Check if all yesterday's daily tasks were completed
            yesterday_all_daily = Task.objects.filter(
                user=user, task_type='daily', is_recurring=True,
                start_time__date=yesterday,
            )
            if yesterday_all_daily.exists() and not yesterday_all_daily.filter(
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.MISSED]
            ).exists():
                user.streak_count += 1
                user.longest_streak = max(user.longest_streak, user.streak_count)

        # --- STEP 6: Create fresh daily tasks for today ---
        _create_today_daily_tasks(user, today)

        # --- STEP 7: Mark as processed ---
        user.last_processed_date = today
        user.save()


def _create_today_daily_tasks(user, today):
    """Create fresh daily task instances for today if they don't exist yet."""

    # Get unique daily task titles
    daily_titles = Task.objects.filter(
        user=user,
        is_recurring=True,
        task_type='daily',
    ).values_list('title', flat=True).distinct()

    for title in daily_titles:
        # Skip titles that start with [Pending] — those are rollover copies
        if title.startswith('[Pending]'):
            continue

        # Skip if any instance for today already exists
        already_exists = Task.objects.filter(
            user=user,
            title=title,
            is_recurring=True,
            task_type='daily',
            start_time__date=today,
        ).exists()

        if already_exists:
            continue

        # Get latest version as template
        template = Task.objects.filter(
            user=user, title=title, is_recurring=True, task_type='daily',
        ).order_by('-created_at').first()

        if template:
            Task.objects.create(
                user=user,
                title=template.title,
                description=template.description,
                task_type='daily',
                priority=Task.Priority.HIGH,
                status=Task.Status.TODO,
                tags=template.tags,
                category=template.category,
                color=template.color,
                icon=template.icon,
                is_recurring=True,
                recurrence_type='daily',
                xp_reward=10,
                penalty_points=template.penalty_points,
                start_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_start_time)
                ),
                end_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_end_time)
                ),
            )


def generate_daily_tasks():
    """Generate today's recurring task instances for all active rules."""
    today = _today()
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
            Task.objects.create(
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

        rule.last_generated = today
        rule.save()


def update_daily_streaks():
    """Update streak records at end of day."""
    today = _today()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    for user in User.objects.all():
        today_tasks = Task.objects.filter(user=user, start_time__date=today)
        total = today_tasks.count()
        completed = today_tasks.filter(status=Task.Status.COMPLETED).count()

        if total == 0:
            continue

        is_perfect = completed == total
        StreakRecord.objects.update_or_create(
            user=user, date=today,
            defaults={
                'tasks_completed': completed,
                'tasks_total': total,
                'is_perfect_day': is_perfect,
            }
        )
