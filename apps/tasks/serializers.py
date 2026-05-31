import zoneinfo
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import Task, Tag

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

# XP rewards by priority for time-based tasks
PRIORITY_XP = {'low': 5, 'medium': 8, 'high': 10, 'urgent': 10}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["user", "completed_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        task_type = validated_data.get("task_type", "daily")
        today = timezone.now().astimezone(IST).date()

        if task_type == "daily":
            # Daily routine: always high priority, +10 XP, -20 XP penalty
            validated_data["priority"] = "high"
            validated_data["xp_reward"] = 10
            validated_data["penalty_points"] = 20
            validated_data["is_recurring"] = True
            validated_data["recurrence_type"] = "daily"
            validated_data.setdefault("start_time", timezone.make_aware(
                timezone.datetime.combine(today, user.day_start_time), IST
            ))
            validated_data.setdefault("end_time", timezone.make_aware(
                timezone.datetime.combine(today, user.day_end_time), IST
            ))

        elif task_type == "timeframe":
            # Time-based: XP based on priority, penalty = 2x XP
            priority = validated_data.get("priority", "medium")
            xp = PRIORITY_XP.get(priority, 8)
            validated_data["xp_reward"] = xp
            validated_data["penalty_points"] = xp * 2

        task = super().create(validated_data)

        # For timeframe tasks, create subtasks (one per day)
        if task_type == "timeframe" and task.timeframe_days:
            start = task.timeframe_start_date or today
            for i in range(task.timeframe_days):
                date = start + timedelta(days=i)
                Task.objects.create(
                    user=task.user,
                    title=f"{task.title} - Day {i + 1}",
                    task_type="timeframe",
                    priority=task.priority,
                    status="todo",
                    parent_task=task,
                    xp_reward=task.xp_reward,
                    penalty_points=task.penalty_points,
                    tags=task.tags,
                    category=task.category,
                    color=task.color,
                    original_date=date,
                    start_time=timezone.make_aware(
                        timezone.datetime.combine(date, user.day_start_time), IST
                    ),
                    end_time=timezone.make_aware(
                        timezone.datetime.combine(date, user.day_end_time), IST
                    ),
                )

        return task
