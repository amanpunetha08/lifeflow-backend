"""
Seed 2-week career + finance plan (June 8 - June 21, 2026)
Usage: python manage.py seed_2week_plan <email>
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

# DSA problems mapped by day (Neetcode 150 order)
WEEK1_DSA = [
    "Contains Duplicate (Neetcode #1 - Arrays)",
    "Valid Anagram (Neetcode #2 - Arrays)",
    "Two Sum (Neetcode #3 - Arrays)",
    "Group Anagrams (Neetcode #4 - Arrays)",
    "Top K Frequent Elements (Neetcode #5 - Arrays)",
    "Product of Array Except Self (Neetcode #6 - Arrays)",
]
WEEK2_DSA = [
    "Valid Palindrome (Neetcode - Two Pointers)",
    "Two Sum II (Neetcode - Two Pointers)",
    "3Sum (Neetcode - Two Pointers)",
    "Container With Most Water (Neetcode - Two Pointers)",
    "Best Time to Buy and Sell Stock (Neetcode - Sliding Window)",
    "Longest Substring Without Repeating (Neetcode - Sliding Window)",
]

# System Design chapters (Alex Xu Vol 1)
WEEK1_SD = [
    "Scale from Zero to Millions (Ch 1)",
    "Back-of-envelope Estimation (Ch 2)",
    "System Design Framework (Ch 3)",
    "Rate Limiter Design (Ch 4)",
    "Consistent Hashing (Ch 5)",
    "Revise Ch 1-5",
]
WEEK2_SD = [
    "Key-Value Store (Ch 6)",
    "Unique ID Generator (Ch 7)",
    "URL Shortener (Ch 8)",
    "Web Crawler (Ch 9)",
    "Notification System (Ch 10)",
    "Revise Ch 6-10",
]

# Finance tasks (Mon-Fri only)
WEEK1_FIN = [
    "Zerodha Varsity Module 1 Ch 1-2: What is stock market",
    "Varsity Module 1 Ch 3-4: Bull/Bear, indices, NSE/BSE",
    "Varsity Module 1 Ch 5-6: Mutual funds, SIP vs lumpsum",
    "Open Zerodha/Groww account (if not done)",
    "Start SIP: ₹5000 in Nifty 50 index fund",
]
WEEK2_FIN = [
    "Expense tracking: list all monthly expenses",
    "Calculate savings rate + investment capacity",
    "Learn PPF, EPF, FD, RD (Varsity/YouTube)",
    "Set up 10L family fund goal: RD ₹40K/month",
    "Research second-hand car: shortlist 2-3 (OLX/Cars24)",
]


class Command(BaseCommand):
    help = "Seed 2-week career + finance plan"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)

    def handle(self, *args, **options):
        user = User.objects.get(email=options["email"])
        created = 0

        for week_offset in range(2):
            dsa_list = WEEK1_DSA if week_offset == 0 else WEEK2_DSA
            sd_list = WEEK1_SD if week_offset == 0 else WEEK2_SD
            fin_list = WEEK1_FIN if week_offset == 0 else WEEK2_FIN

            week_start = PLAN_START + timedelta(weeks=week_offset)
            fin_idx = 0

            for day_offset in range(6):  # Mon-Sat (6 days)
                d = week_start + timedelta(days=day_offset)
                is_weekday = day_offset < 5

                # DSA task (Mon-Sat)
                Task.objects.create(
                    user=user,
                    title=f"DSA: {dsa_list[day_offset]}",
                    description="Solve on LeetCode. If stuck >20min, study solution, then re-implement from scratch.",
                    task_type="daily",
                    priority="high",
                    status="todo",
                    is_recurring=True,
                    recurrence_type="daily",
                    xp_reward=15,
                    penalty_points=25,
                    tags=["career", "dsa"],
                    category="Career Growth",
                    color="#6366f1",
                    start_time=timezone.make_aware(datetime.combine(d, time(7, 40)), IST),
                    end_time=timezone.make_aware(datetime.combine(d, time(8, 20)), IST),
                    notes="TRAP Log:\n• Topic:\n• Approach:\n• Pattern:\n• Review needed: Y/N",
                )
                created += 1

                # System Design task (Mon-Sat)
                Task.objects.create(
                    user=user,
                    title=f"SD: {sd_list[day_offset]}",
                    description="Read chapter/section. After reading, close book and draw system from memory.",
                    task_type="daily",
                    priority="high",
                    status="todo",
                    is_recurring=True,
                    recurrence_type="daily",
                    xp_reward=12,
                    penalty_points=20,
                    tags=["career", "system-design"],
                    category="Career Growth",
                    color="#8b5cf6",
                    start_time=timezone.make_aware(datetime.combine(d, time(8, 25)), IST),
                    end_time=timezone.make_aware(datetime.combine(d, time(8, 55)), IST),
                    notes="Key concepts:\n•\nCould I explain this in interview? Y/N",
                )
                created += 1

                # Finance task (Mon-Fri only)
                if is_weekday:
                    Task.objects.create(
                        user=user,
                        title=f"Finance: {fin_list[fin_idx]}",
                        description="30 min evening block. Learn + take action.",
                        task_type="timeframe",
                        priority="medium",
                        status="todo",
                        xp_reward=10,
                        penalty_points=15,
                        tags=["finance"],
                        category="Financial Growth",
                        color="#10b981",
                        start_time=timezone.make_aware(datetime.combine(d, time(20, 0)), IST),
                        end_time=timezone.make_aware(datetime.combine(d, time(20, 30)), IST),
                        notes="What I learned:\n•\nAction taken:",
                    )
                    fin_idx += 1
                    created += 1

            # Sunday review task
            sunday = week_start + timedelta(days=6)
            Task.objects.create(
                user=user,
                title=f"Week {week_offset + 1} Review: Revise all DSA problems",
                description="Re-solve any problem you struggled with. No new problems.",
                task_type="daily",
                priority="medium",
                status="todo",
                xp_reward=20,
                penalty_points=10,
                tags=["career", "review"],
                category="Career Growth",
                color="#f59e0b",
                start_time=timezone.make_aware(datetime.combine(sunday, time(8, 0)), IST),
                end_time=timezone.make_aware(datetime.combine(sunday, time(9, 30)), IST),
                notes="Problems re-solved:\n•\nWeak areas to revisit next week:",
            )
            created += 1

        # Daily routine tasks (wake up, no phone, log) - create for all 14 days
        for i in range(14):
            d = PLAN_START + timedelta(days=i)
            Task.objects.create(
                user=user,
                title="Morning: Wake + Water + Stretch (NO PHONE)",
                task_type="daily",
                priority="high",
                status="todo",
                is_recurring=True,
                recurrence_type="daily",
                xp_reward=5,
                penalty_points=10,
                tags=["routine", "health"],
                category="Daily Routine",
                color="#f97316",
                start_time=timezone.make_aware(datetime.combine(d, time(7, 30)), IST),
                end_time=timezone.make_aware(datetime.combine(d, time(7, 40)), IST),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} tasks for {user.email}"))
