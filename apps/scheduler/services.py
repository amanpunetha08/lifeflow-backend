import zoneinfo
from django.utils import timezone
from apps.tasks.models import Task
from apps.gamification.models import XPLog

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


def process_expired_tasks(user):
    """
    Runs once per day (guarded by last_processed_date).
    1. Find all pending tasks from before today
    2. Daily routine not completed: -20 XP demerit, mark missed
    3. Time-based not completed: -2x assigned XP demerit, mark missed
    4. Create fresh daily routine tasks for today
    """
    today = timezone.now().astimezone(IST).date()

    if user.last_processed_date == today:
        return {"status": "already_processed"}

    timezone.activate(IST)

    # --- Step 1: Get all pending tasks from before today ---
    pending = Task.objects.filter(
        user=user,
        status__in=["todo", "in_progress"],
        start_time__date__lt=today,
    )

    for task in pending:
        # Mark as missed
        task.status = "missed"
        task.save()

        # Apply demerit: penalty_points is already set correctly
        # Daily: 20, Time-based: 2x XP (10, 16, or 20)
        penalty = task.penalty_points or 20
        user.discipline_score = max(0, user.discipline_score - 2)
        user.chaos_meter = min(100, user.chaos_meter + 3)
        user.streak_count = 0

        XPLog.objects.create(
            user=user, amount=-penalty,
            reason=f"Missed: {task.title} (-{penalty} XP)", task=task
        )

    # --- Step 2: Create fresh daily routine tasks for today ---
    # Find unique daily recurring task titles
    daily_titles = list(
        Task.objects.filter(
            user=user, is_recurring=True, task_type="daily",
        ).values_list("title", flat=True).distinct()
    )

    for title in daily_titles:
        # Skip if today's instance already exists
        exists = Task.objects.filter(
            user=user, title=title, task_type="daily",
            start_time__date=today,
        ).exists()

        if exists:
            continue

        # Get template (latest version)
        template = Task.objects.filter(
            user=user, title=title, is_recurring=True, task_type="daily",
        ).order_by("-created_at").first()

        if template:
            Task.objects.create(
                user=user,
                title=template.title,
                description=template.description,
                task_type="daily",
                priority="high",
                status="todo",
                is_recurring=True,
                recurrence_type="daily",
                xp_reward=10,
                penalty_points=20,
                tags=template.tags,
                category=template.category,
                color=template.color,
                start_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_start_time), IST
                ),
                end_time=timezone.make_aware(
                    timezone.datetime.combine(today, user.day_end_time), IST
                ),
            )

    # --- Step 3: Update user ---
    user.last_processed_date = today
    user.save()

    timezone.deactivate()
    return {"status": "processed", "date": str(today)}
