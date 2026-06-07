"""
Seed 2-week home workout plan (progressive, minimal equipment)
Usage: python manage.py seed_workout_plan <email>
"""
import zoneinfo
from datetime import date, time, timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

PLAN_START = date(2026, 6, 8)  # Monday

# Week 1: Foundation (low volume, build habit)
# Only 3 days: Mon/Wed/Fri — rest days between
WEEK1_WORKOUTS = {
    0: "Day A: Push (8 push-ups × 2 sets, 30s plank × 2, 10 squats × 2)",
    2: "Day B: Pull (1 pull-up × 3 attempts, 10 inverted rows/doorframe, 15s hang × 2)",
    4: "Day A: Push (10 push-ups × 2 sets, 35s plank × 2, 12 squats × 2)",
}

# Week 2: Slight progression
WEEK2_WORKOUTS = {
    0: "Day A: Push (10 push-ups × 3 sets, 40s plank × 2, 15 squats × 2)",
    2: "Day B: Pull (1-2 pull-ups × 3, 12 inverted rows, 20s hang × 2)",
    4: "Day C: Legs (20 squats × 3, 10 lunges each leg × 2, 30 calf raises × 2)",
    5: "Day A: Push (12 push-ups × 3, 45s plank × 2, 10 diamond push-ups × 2)",
}

WORKOUT_DESC = """Home workout — NO gym needed.
Equipment: Your body + a pull-up bar (doorframe one ₹500) or sturdy door.

Rules:
• Rest 60-90 sec between sets
• If you can't complete reps, do as many as possible (AMRAP)
• Log how many reps you actually did in notes
• 5 min warm-up: jumping jacks + arm circles + hip rotations"""


class Command(BaseCommand):
    help = "Seed 2-week home workout plan"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)

    def handle(self, *args, **options):
        user = User.objects.get(email=options["email"])
        created = 0

        for week_offset in range(2):
            workouts = WEEK1_WORKOUTS if week_offset == 0 else WEEK2_WORKOUTS
            week_start = PLAN_START + timedelta(weeks=week_offset)

            for day_offset, title in workouts.items():
                d = week_start + timedelta(days=day_offset)
                Task.objects.create(
                    user=user,
                    title=f"Workout: {title}",
                    description=WORKOUT_DESC,
                    task_type="daily",
                    priority="high",
                    status="todo",
                    is_recurring=True,
                    recurrence_type="daily",
                    xp_reward=20,
                    penalty_points=30,
                    tags=["health", "workout"],
                    category="Health",
                    color="#ef4444",
                    start_time=timezone.make_aware(datetime.combine(d, time(18, 30)), IST),
                    end_time=timezone.make_aware(datetime.combine(d, time(19, 0)), IST),
                    notes="Reps completed:\n• Set 1:\n• Set 2:\n• Set 3:\nEnergy level (1-5):\nSoreness:",
                )
                created += 1

        # Daily 10-min walk task (all 14 days)
        for i in range(14):
            d = PLAN_START + timedelta(days=i)
            Task.objects.create(
                user=user,
                title="Evening Walk: 10 min minimum (no phone)",
                task_type="daily",
                priority="medium",
                status="todo",
                is_recurring=True,
                recurrence_type="daily",
                xp_reward=5,
                penalty_points=5,
                tags=["health", "walk"],
                category="Health",
                color="#f97316",
                start_time=timezone.make_aware(datetime.combine(d, time(19, 30)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(19, 40)), IST),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} workout tasks for {user.email}"))
