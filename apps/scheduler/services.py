import zoneinfo
from datetime import timedelta, time, datetime
from django.utils import timezone
from apps.tasks.models import Task
from apps.gamification.models import XPLog

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


def seed_2week_plan(user):
    """Create/reset the 2-week career + fitness + finance plan for any user."""
    today = timezone.now().astimezone(IST).date()
    plan_start = today + timedelta(days=1)
    plan_end = plan_start + timedelta(days=11)

    # Delete existing future plan tasks (acts as reset)
    Task.objects.filter(
        user=user, category__in=["Career Growth", "Financial Growth", "Health", "Daily Routine"],
        start_time__date__gte=plan_start
    ).delete()

    DSA = ['Contains Duplicate (Arrays)', 'Valid Anagram (Arrays)', 'Two Sum (Arrays)',
           'Group Anagrams (Arrays)', 'Top K Frequent (Arrays)', 'Product of Array Except Self',
           'Valid Palindrome (Two Pointers)', 'Two Sum II (Two Pointers)', '3Sum (Two Pointers)',
           'Container With Most Water', 'Best Time Buy/Sell Stock', 'Longest Substring No Repeat']
    SD = ['Scale from Zero to Millions (Ch 1)', 'Back-of-envelope Estimation (Ch 2)', 'System Design Framework (Ch 3)',
          'Rate Limiter Design (Ch 4)', 'Consistent Hashing (Ch 5)', 'Revise Ch 1-5',
          'Key-Value Store (Ch 6)', 'Unique ID Generator (Ch 7)', 'URL Shortener (Ch 8)',
          'Web Crawler (Ch 9)', 'Notification System (Ch 10)', 'Revise Ch 6-10']
    WORKOUTS = {0: 'Push: 10 push-ups×3, 30s plank×2, 12 squats×2',
                2: 'Pull: 1-2 pull-ups×3, 10 inverted rows, 15s hang×2',
                4: 'Push: 12 push-ups×3, 40s plank×2, 15 squats×2',
                5: 'Legs: 20 squats×3, 10 lunges each×2, 30 calf raises×2',
                7: 'Push: 15 push-ups×3, 45s plank×2, diamond push-ups×2',
                9: 'Pull: 2 pull-ups×3, 12 inverted rows, 20s hang×3',
                11: 'Full: 12 push-ups×2, 1 pull-up×3, 15 squats×3, plank 45s×2'}
    FINANCE_SUNDAY = ['Zerodha Varsity Module 1 (Ch 1-4) + Open account',
                      'Expense tracking + SIP setup + RD research']

    created = 0
    for i in range(12):
        d = plan_start + timedelta(days=i)
        is_sunday = d.weekday() == 6

        Task.objects.create(user=user, title='⏰ 7:00 — Wake + Water + Stretch (NO PHONE)',
            task_type='daily', priority='high', status='todo', is_recurring=True, recurrence_type='daily',
            xp_reward=5, penalty_points=10, tags=['routine'], category='Daily Routine', color='#f97316',
            start_time=timezone.make_aware(datetime.combine(d, time(7, 0)), IST),
            end_time=timezone.make_aware(datetime.combine(d, time(7, 10)), IST))
        Task.objects.create(user=user, title=f'📚 7:10-7:50 — DSA: {DSA[i]}',
            description='Solve on LeetCode. Stuck >20min? Study solution, re-implement.',
            task_type='daily', priority='high', status='todo', is_recurring=True, recurrence_type='daily',
            xp_reward=15, penalty_points=25, tags=['career', 'dsa'], category='Career Growth', color='#6366f1',
            start_time=timezone.make_aware(datetime.combine(d, time(7, 10)), IST),
            end_time=timezone.make_aware(datetime.combine(d, time(7, 50)), IST),
            notes='TRAP Log:\n• Topic:\n• Approach:\n• Pattern:\n• Review needed: Y/N')
        Task.objects.create(user=user, title=f'🧠 7:50-8:10 — SD: {SD[i]}',
            description='Read 5-6 pages. Close book, recall from memory.',
            task_type='daily', priority='high', status='todo', is_recurring=True, recurrence_type='daily',
            xp_reward=12, penalty_points=20, tags=['career', 'system-design'], category='Career Growth', color='#8b5cf6',
            start_time=timezone.make_aware(datetime.combine(d, time(7, 50)), IST),
            end_time=timezone.make_aware(datetime.combine(d, time(8, 10)), IST),
            notes='Key concepts:\n•\nCould I explain this in interview? Y/N')
        created += 3

        if i in WORKOUTS:
            Task.objects.create(user=user, title=f'💪 6:30 PM — Workout: {WORKOUTS[i]}',
                description='Home. 5 min warm-up. Rest 60-90s. AMRAP if cant finish.',
                task_type='daily', priority='high', status='todo', is_recurring=True, recurrence_type='daily',
                xp_reward=20, penalty_points=30, tags=['health', 'workout'], category='Health', color='#ef4444',
                start_time=timezone.make_aware(datetime.combine(d, time(18, 30)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(18, 50)), IST),
                notes='Reps completed:\n• Set 1:\n• Set 2:\n• Set 3:\nEnergy (1-5):')
            created += 1

        if not is_sunday:
            Task.objects.create(user=user, title='🚶 1:00 PM — Lunch Break Walk (10 min, no phone)',
                task_type='daily', priority='medium', status='todo', is_recurring=True, recurrence_type='daily',
                xp_reward=5, penalty_points=5, tags=['health', 'walk'], category='Health', color='#f97316',
                start_time=timezone.make_aware(datetime.combine(d, time(13, 0)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(13, 10)), IST))
            created += 1

        Task.objects.create(user=user, title='🍽️ Before Sleep — Log meals',
            task_type='daily', priority='medium', status='todo', is_recurring=True, recurrence_type='daily',
            xp_reward=5, penalty_points=10, tags=['health', 'diet'], category='Health', color='#10b981',
            start_time=timezone.make_aware(datetime.combine(d, time(22, 30)), IST),
            end_time=timezone.make_aware(datetime.combine(d, time(22, 35)), IST),
            notes='☐ Breakfast: oats/poha + 2 eggs + almonds\n☐ Lunch: roti + paneer/dal + salad\n☐ Dinner: roti + dal + salad\n☐ Water: 4L\n\nActual:')
        created += 1

        if is_sunday:
            week_num = 0 if i < 7 else 1
            Task.objects.create(user=user, title=f'💰 Sunday 11 AM — Finance: {FINANCE_SUNDAY[week_num]}',
                description='1 hour batch. Learn + take action.',
                task_type='timeframe', priority='medium', status='todo',
                xp_reward=20, penalty_points=15, tags=['finance'], category='Financial Growth', color='#10b981',
                start_time=timezone.make_aware(datetime.combine(d, time(11, 0)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(12, 0)), IST),
                notes='What I learned:\n•\nAction taken:\n•')
            created += 1

    return {"status": "reset_and_created", "tasks": created, "start_date": str(plan_start), "end_date": str(plan_end)}


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
