import zoneinfo
from datetime import timedelta
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.tasks.models import Task
from apps.gamification.models import XPLog, StreakRecord

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


class ProgressReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now().astimezone(IST)
        today = now.date()
        days = int(request.query_params.get("days", 2))
        start_date = today - timedelta(days=days - 1)

        timezone.activate(IST)
        tasks = Task.objects.filter(user=user, start_time__date__gte=start_date, start_time__date__lte=today)

        # Per-day breakdown
        daily = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            day_tasks = tasks.filter(start_time__date=d)
            completed = day_tasks.filter(status="completed")
            missed = day_tasks.filter(status="missed")
            pending = day_tasks.filter(status__in=["todo", "in_progress"])

            day_data = {
                "date": str(d),
                "total": day_tasks.count(),
                "completed": completed.count(),
                "missed": missed.count(),
                "pending": pending.count(),
                "completion_rate": round(completed.count() / max(day_tasks.count(), 1) * 100),
                "tasks": []
            }

            for t in day_tasks.order_by("start_time"):
                day_data["tasks"].append({
                    "title": t.title,
                    "status": t.status,
                    "category": t.category,
                    "xp_reward": t.xp_reward,
                    "notes": t.notes or "",
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                })

            daily.append(day_data)

        # Category breakdown
        categories = {}
        for cat in tasks.values_list("category", flat=True).distinct():
            cat_tasks = tasks.filter(category=cat)
            categories[cat] = {
                "total": cat_tasks.count(),
                "completed": cat_tasks.filter(status="completed").count(),
                "rate": round(cat_tasks.filter(status="completed").count() / max(cat_tasks.count(), 1) * 100),
            }

        # Notes summary (non-empty notes from completed tasks)
        notes_data = list(
            tasks.filter(notes__gt="", status="completed")
            .values("title", "notes", "category", "start_time")
            .order_by("start_time")
        )
        for n in notes_data:
            n["date"] = n.pop("start_time").astimezone(IST).strftime("%Y-%m-%d")

        # XP earned in period
        xp_earned = XPLog.objects.filter(user=user, created_at__date__gte=start_date, amount__gt=0).aggregate(s=Sum("amount"))["s"] or 0

        timezone.deactivate()
        return Response({
            "period": {"start": str(start_date), "end": str(today), "days": days},
            "summary": {
                "total_tasks": tasks.count(),
                "completed": tasks.filter(status="completed").count(),
                "missed": tasks.filter(status="missed").count(),
                "pending": tasks.filter(status__in=["todo", "in_progress"]).count(),
                "completion_rate": round(tasks.filter(status="completed").count() / max(tasks.count(), 1) * 100),
                "xp_earned": xp_earned,
                "streak": user.streak_count,
                "level": user.level,
            },
            "categories": categories,
            "daily": daily,
            "notes_log": notes_data,
        })


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now().astimezone(IST)
        today = now.date()
        timezone.activate(IST)
        week_start = today - timedelta(days=6)  # Last 7 days
        week_end = today
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start - timedelta(days=1)

        # Last 7 days tasks
        week_tasks = Task.objects.filter(user=user, start_time__date__gte=week_start, start_time__date__lte=week_end)
        last_week_tasks = Task.objects.filter(user=user, start_time__date__gte=last_week_start, start_time__date__lte=last_week_end)

        completed_this_week = week_tasks.filter(status="completed").count()
        total_this_week = week_tasks.count()
        completed_last_week = last_week_tasks.filter(status="completed").count()
        total_last_week = last_week_tasks.count()

        focus_this_week = week_tasks.filter(actual_duration__isnull=False).aggregate(s=Sum("actual_duration"))["s"] or 0
        focus_last_week = last_week_tasks.filter(actual_duration__isnull=False).aggregate(s=Sum("actual_duration"))["s"] or 0

        productivity = int(completed_this_week / total_this_week * 100) if total_this_week else 0
        productivity_last = int(completed_last_week / total_last_week * 100) if total_last_week else 0

        xp_today = XPLog.objects.filter(user=user, created_at__date=today, amount__gt=0).aggregate(s=Sum("amount"))["s"] or 0

        def pct_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round((current - previous) / previous * 100, 1)

        stats = {
            "tasks_completed": completed_this_week,
            "tasks_total": total_this_week,
            "focus_time_minutes": focus_this_week,
            "productivity_score": productivity,
            "xp_earned_today": xp_today,
            "discipline_score": float(user.discipline_score),
            "tasks_completed_change": pct_change(completed_this_week, completed_last_week),
            "focus_time_change": pct_change(focus_this_week, focus_last_week),
            "productivity_change": pct_change(productivity, productivity_last),
            "discipline_change": 0.0,
        }

        # Weekly trend
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_trend = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            day_tasks = week_tasks.filter(start_time__date=d)
            day_total = day_tasks.count()
            day_completed = day_tasks.filter(status="completed").count()
            score = int(day_completed / day_total * 100) if day_total else 0
            weekly_trend.append({"day": day_names[d.weekday()], "tasks": day_completed, "score": score})

        # Task breakdown
        task_breakdown = {
            "completed": week_tasks.filter(status="completed").count(),
            "in_progress": week_tasks.filter(status="in_progress").count(),
            "todo": week_tasks.filter(status="todo").count(),
            "missed": week_tasks.filter(status="missed").count(),
        }

        # Habit consistency
        habits = Task.objects.filter(user=user, is_recurring=True, recurrence_type="daily").values_list("title", flat=True).distinct()
        habit_consistency = []
        for title in habits:
            completed_days = Task.objects.filter(
                user=user, title=title, is_recurring=True, status="completed",
                start_time__date__gte=week_start, start_time__date__lte=week_end
            ).values("start_time__date").distinct().count()
            habit_consistency.append({"name": title, "completed": completed_days, "total": 7})

        # Daily XP
        daily_xp = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            xp = XPLog.objects.filter(user=user, created_at__date=d, amount__gt=0).aggregate(s=Sum("amount"))["s"] or 0
            daily_xp.append({"day": day_names[d.weekday()], "xp": xp})

        # Streak history
        # Streak history - build from actual tasks (last 90 days) using single query
        ninety_days_ago = today - timedelta(days=90)
        from django.db.models.functions import TruncDate
        streak_data = (
            Task.objects.filter(user=user, start_time__date__gte=ninety_days_ago)
            .values(day=TruncDate('start_time'))
            .annotate(total=Count('id'), completed=Count('id', filter=Q(status='completed')))
            .order_by('day')
        )
        streak_history = [
            {"date": str(r["day"]), "completed": r["completed"], "total": r["total"]}
            for r in streak_data if r["total"] > 0
        ]

        timezone.deactivate()
        return Response({
            "stats": stats,
            "weekly_trend": weekly_trend,
            "task_breakdown": task_breakdown,
            "habit_consistency": habit_consistency,
            "daily_xp": daily_xp,
            "streak_history": streak_history,
        })
