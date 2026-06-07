import zoneinfo
from datetime import timedelta, time, datetime
from django.utils import timezone
from apps.tasks.models import Task
from apps.gamification.models import XPLog

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


def seed_2week_plan(user):
    """Create the 2-week career + fitness + finance plan for any user."""
    today = timezone.now().astimezone(IST).date()
    plan_start = today + timedelta(days=1)  # Start tomorrow

    # Check if plan already exists
    existing = Task.objects.filter(
        user=user, category__in=["Career Growth", "Financial Growth", "Health"],
        start_time__date__gte=plan_start, start_time__date__lte=plan_start + timedelta(days=13)
    ).count()
    if existing > 10:
        return {"status": "already_seeded", "tasks": existing}

    WEEK1_DSA = ["Contains Duplicate (Arrays)", "Valid Anagram (Arrays)", "Two Sum (Arrays)",
                 "Group Anagrams (Arrays)", "Top K Frequent Elements (Arrays)", "Product of Array Except Self (Arrays)"]
    WEEK2_DSA = ["Valid Palindrome (Two Pointers)", "Two Sum II (Two Pointers)", "3Sum (Two Pointers)",
                 "Container With Most Water (Two Pointers)", "Best Time to Buy/Sell Stock (Sliding Window)", "Longest Substring Without Repeating (Sliding Window)"]
    WEEK1_SD = ["Scale from Zero to Millions (Ch 1)", "Back-of-envelope Estimation (Ch 2)", "System Design Framework (Ch 3)",
                "Rate Limiter Design (Ch 4)", "Consistent Hashing (Ch 5)", "Revise Ch 1-5"]
    WEEK2_SD = ["Key-Value Store (Ch 6)", "Unique ID Generator (Ch 7)", "URL Shortener (Ch 8)",
                "Web Crawler (Ch 9)", "Notification System (Ch 10)", "Revise Ch 6-10"]
    WEEK1_FIN = ["Stock market basics (Zerodha Varsity Module 1)", "Bull/Bear, indices, NSE/BSE",
                 "Mutual funds, SIP vs lumpsum", "Open investment account", "Start SIP: ₹5000 index fund"]
    WEEK2_FIN = ["Expense tracking: list monthly expenses", "Calculate savings rate",
                 "Learn PPF, EPF, FD, RD", "Set up family fund goal", "Research goals + shortlist actions"]
    WEEK1_WO = {0: "Push (8 push-ups×2, 30s plank×2, 10 squats×2)",
                2: "Pull (1 pull-up×3, 10 inverted rows, 15s hang×2)",
                4: "Push (10 push-ups×2, 35s plank×2, 12 squats×2)"}
    WEEK2_WO = {0: "Push (10 push-ups×3, 40s plank×2, 15 squats×2)",
                2: "Pull (1-2 pull-ups×3, 12 inverted rows, 20s hang×2)",
                4: "Legs (20 squats×3, 10 lunges each×2, 30 calf raises×2)",
                5: "Push (12 push-ups×3, 45s plank×2, diamond push-ups×2)"}

    created = 0
    for week in range(2):
        dsa = WEEK1_DSA if week == 0 else WEEK2_DSA
        sd = WEEK1_SD if week == 0 else WEEK2_SD
        fin = WEEK1_FIN if week == 0 else WEEK2_FIN
        wo = WEEK1_WO if week == 0 else WEEK2_WO
        week_start = plan_start + timedelta(weeks=week)
        fin_idx = 0

        for day in range(6):
            d = week_start + timedelta(days=day)
            # Morning routine
            Task.objects.create(user=user, title="Morning: Wake + Water + Stretch (NO PHONE)",
                task_type="daily", priority="high", status="todo", is_recurring=True, recurrence_type="daily",
                xp_reward=5, penalty_points=10, tags=["routine", "health"], category="Daily Routine", color="#f97316",
                start_time=timezone.make_aware(datetime.combine(d, time(7, 30)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(7, 40)), IST))
            # DSA
            Task.objects.create(user=user, title=f"DSA: {dsa[day]}",
                description="Solve on LeetCode. If stuck >20min, study solution, then re-implement.",
                task_type="daily", priority="high", status="todo", is_recurring=True, recurrence_type="daily",
                xp_reward=15, penalty_points=25, tags=["career", "dsa"], category="Career Growth", color="#6366f1",
                start_time=timezone.make_aware(datetime.combine(d, time(7, 40)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(8, 20)), IST),
                notes="TRAP Log:\n• Topic:\n• Approach:\n• Pattern:\n• Review needed: Y/N")
            # System Design (in office, first 30 min after reaching)
            Task.objects.create(user=user, title=f"SD: {sd[day]}",
                description="Read section. Close book, draw system from memory.",
                task_type="daily", priority="high", status="todo", is_recurring=True, recurrence_type="daily",
                xp_reward=12, penalty_points=20, tags=["career", "system-design"], category="Career Growth", color="#8b5cf6",
                start_time=timezone.make_aware(datetime.combine(d, time(9, 0)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(9, 30)), IST),
                notes="Key concepts:\n•\nCould I explain this in interview? Y/N")
            created += 3
            # Workout (select days only)
            if day in wo:
                Task.objects.create(user=user, title=f"Workout: {wo[day]}",
                    description="Home workout. 5 min warm-up. Rest 60-90s between sets. Log reps in notes.",
                    task_type="daily", priority="high", status="todo", is_recurring=True, recurrence_type="daily",
                    xp_reward=20, penalty_points=30, tags=["health", "workout"], category="Health", color="#ef4444",
                    start_time=timezone.make_aware(datetime.combine(d, time(18, 30)), IST),
                    end_time=timezone.make_aware(datetime.combine(d, time(19, 0)), IST),
                    notes="Reps completed:\n• Set 1:\n• Set 2:\n• Set 3:\nEnergy (1-5):")
                created += 1
            # Evening walk
            Task.objects.create(user=user, title="Evening Walk: 10 min (no phone)",
                task_type="daily", priority="medium", status="todo", is_recurring=True, recurrence_type="daily",
                xp_reward=5, penalty_points=5, tags=["health", "walk"], category="Health", color="#f97316",
                start_time=timezone.make_aware(datetime.combine(d, time(19, 30)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(19, 40)), IST))
            # Diet tracking
            Task.objects.create(user=user, title="Diet: Track all meals today",
                task_type="daily", priority="medium", status="todo", is_recurring=True, recurrence_type="daily",
                xp_reward=5, penalty_points=10, tags=["health", "diet"], category="Health", color="#10b981",
                start_time=timezone.make_aware(datetime.combine(d, time(21, 0)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(21, 5)), IST),
                notes="Check off what you ate:\n☐ Breakfast (8:20): 30g oats/poha + 2 eggs + 20 almonds\n☐ Lunch (1PM): 4 roti/400g rice + 100g paneer + ghee + salad\n☐ Evening (5:30): 1 glass milk + banana\n☐ Dinner (8:30): 3 roti/300g rice + 1 katori dal + salad\n☐ Water: 4 litres\n\nMissed/replaced:")
            created += 2
            # Finance (weekdays only)
            if day < 5:
                Task.objects.create(user=user, title=f"Finance: {fin[fin_idx]}",
                    description="30 min evening block. Learn + take action.",
                    task_type="timeframe", priority="medium", status="todo",
                    xp_reward=10, penalty_points=15, tags=["finance"], category="Financial Growth", color="#10b981",
                    start_time=timezone.make_aware(datetime.combine(d, time(20, 0)), IST),
                    end_time=timezone.make_aware(datetime.combine(d, time(20, 30)), IST),
                    notes="What I learned:\n•\nAction taken:")
                fin_idx += 1
                created += 1

        # Sunday review
        sunday = week_start + timedelta(days=6)
        Task.objects.create(user=user, title=f"Week {week+1} Review: Revise all DSA problems",
            description="Re-solve problems you struggled with. No new problems.",
            task_type="daily", priority="medium", status="todo",
            xp_reward=20, penalty_points=10, tags=["career", "review"], category="Career Growth", color="#f59e0b",
            start_time=timezone.make_aware(datetime.combine(sunday, time(8, 0)), IST),
            end_time=timezone.make_aware(datetime.combine(sunday, time(9, 30)), IST),
            notes="Problems re-solved:\n•\nWeak areas:")
        Task.objects.create(user=user, title="Morning: Wake + Water + Stretch (NO PHONE)",
            task_type="daily", priority="high", status="todo", is_recurring=True, recurrence_type="daily",
            xp_reward=5, penalty_points=10, tags=["routine", "health"], category="Daily Routine", color="#f97316",
            start_time=timezone.make_aware(datetime.combine(sunday, time(7, 30)), IST),
            end_time=timezone.make_aware(datetime.combine(sunday, time(7, 40)), IST))
        Task.objects.create(user=user, title="Evening Walk: 10 min (no phone)",
            task_type="daily", priority="medium", status="todo", is_recurring=True, recurrence_type="daily",
            xp_reward=5, penalty_points=5, tags=["health", "walk"], category="Health", color="#f97316",
            start_time=timezone.make_aware(datetime.combine(sunday, time(19, 30)), IST),
            end_time=timezone.make_aware(datetime.combine(sunday, time(19, 40)), IST))
        created += 3

    return {"status": "created", "tasks": created, "start_date": str(plan_start), "end_date": str(plan_start + timedelta(days=13))}


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
