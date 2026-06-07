import zoneinfo
from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        from apps.gamification.models import XPLog
        task = self.get_object()
        task.status = "completed"
        task.completed_at = timezone.now()
        task.completion_percentage = 100
        task.save()
        user = request.user
        user.add_xp(task.xp_reward)
        user.coins += max(1, task.xp_reward // 2)
        user.total_completed_tasks += 1
        user.discipline_score = min(100, user.discipline_score + 1)
        user.chaos_meter = max(0, user.chaos_meter - 1)
        user.save()
        XPLog.objects.create(user=user, amount=task.xp_reward, reason=f"Completed: {task.title}", task=task)
        return Response(TaskSerializer(task).data)

    @action(detail=False, methods=["get"])
    def today(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            from datetime import datetime as dt
            target_date = dt.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().astimezone(IST).date()
        timezone.activate(IST)
        tasks = self.get_queryset().filter(
            start_time__date=target_date
        ).exclude(status='missed').exclude(
            task_type='timeframe', timeframe_days__isnull=False
        )
        timezone.deactivate()
        return Response(TaskSerializer(tasks, many=True).data)

    @action(detail=False, methods=["post"])
    def reset_today(self, request):
        """Reset tasks for today: apply demerits, recreate daily + missed time-based tasks."""
        user = request.user
        today = timezone.now().astimezone(IST).date()
        timezone.activate(IST)

        # 1. Get all pending tasks from today
        pending = Task.objects.filter(user=user, start_time__date=today, status__in=['todo', 'in_progress'])

        # 2. Mark them missed and apply demerits
        for task in pending:
            task.status = 'missed'
            task.save()
            user.discipline_score = max(0, user.discipline_score - 2)
            user.chaos_meter = min(100, user.chaos_meter + 3)

        # 3. Recreate daily routine tasks for today
        daily_titles = list(Task.objects.filter(
            user=user, is_recurring=True, task_type='daily'
        ).values_list('title', flat=True).distinct())

        created = []
        for title in daily_titles:
            template = Task.objects.filter(
                user=user, title=title, is_recurring=True, task_type='daily'
            ).order_by('-created_at').first()
            if template:
                t = Task.objects.create(
                    user=user, title=template.title, description=template.description,
                    task_type='daily', priority='high', status='todo',
                    is_recurring=True, recurrence_type='daily',
                    xp_reward=10, penalty_points=20,
                    tags=template.tags, category=template.category, color=template.color,
                    start_time=timezone.make_aware(timezone.datetime.combine(today, user.day_start_time), IST),
                    end_time=timezone.make_aware(timezone.datetime.combine(today, user.day_end_time), IST),
                )
                created.append(t.title)

        # 4. Recreate missed time-based tasks for today
        missed_timeframe = Task.objects.filter(
            user=user, task_type='timeframe', status='missed', start_time__date=today
        )
        for task in missed_timeframe:
            t = Task.objects.create(
                user=user, title=task.title, description=task.description,
                task_type='timeframe', priority=task.priority, status='todo',
                xp_reward=task.xp_reward, penalty_points=task.penalty_points,
                tags=task.tags, category=task.category, color='#ef4444',
                is_rolled_over=True, rollover_count=task.rollover_count + 1,
                parent_task=task.parent_task,
                start_time=timezone.make_aware(timezone.datetime.combine(today, user.day_start_time), IST),
                end_time=timezone.make_aware(timezone.datetime.combine(today, user.day_end_time), IST),
            )
            created.append(t.title)

        user.streak_count = 0
        user.save()
        timezone.deactivate()

        return Response({'status': 'reset', 'created': created, 'missed_count': pending.count()})

    @action(detail=False, methods=["get"])
    def missed(self, request):
        tasks = self.get_queryset().filter(status="missed")
        return Response(TaskSerializer(tasks, many=True).data)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now().astimezone(IST)
        today = now.date()
        week_start = today - timedelta(days=today.weekday())

        habits = Task.objects.filter(user=user, is_recurring=True, recurrence_type="daily").values_list("title", flat=True).distinct()
        result = []
        for title in habits:
            # Weekly completion per day (Mon-Sun)
            weekly = []
            for i in range(7):
                d = week_start + timedelta(days=i)
                done = Task.objects.filter(user=user, title=title, is_recurring=True, status="completed", start_time__date=d).exists()
                weekly.append(done)

            # Current streak
            streak = 0
            check_date = today
            while True:
                if Task.objects.filter(user=user, title=title, is_recurring=True, status="completed", start_time__date=check_date).exists():
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break

            total_completed = Task.objects.filter(user=user, title=title, is_recurring=True, status="completed").count()
            result.append({"title": title, "streak": streak, "weekly": weekly, "total_completed": total_completed})

        return Response(result)
