from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'original_date', 'is_rolled_over', 'rollover_count', 'xp_reward')


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    pending_subtasks_count = serializers.ReadOnlyField()
    total_subtasks_count = serializers.ReadOnlyField()
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('user', 'completed_at', 'is_rolled_over', 'rollover_count', 'timeframe_end_date')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        user = validated_data['user']
        task_type = validated_data.get('task_type', 'daily')

        if task_type == 'daily':
            validated_data['is_recurring'] = True
            validated_data['recurrence_type'] = 'daily'
            validated_data['priority'] = Task.Priority.HIGH
            validated_data['xp_reward'] = 10
            # Schedule using user's day times
            today = timezone.now().date()
            validated_data['start_time'] = timezone.make_aware(
                timezone.datetime.combine(today, user.day_start_time)
            )
            validated_data['end_time'] = timezone.make_aware(
                timezone.datetime.combine(today, user.day_end_time)
            )

        elif task_type == 'timeframe':
            days = validated_data.get('timeframe_days', 1)
            start_date = validated_data.get('timeframe_start_date') or timezone.now().date()
            validated_data['timeframe_start_date'] = start_date
            validated_data['timeframe_end_date'] = start_date + timedelta(days=days - 1)
            validated_data['xp_reward'] = 10

        task = super().create(validated_data)

        # For timeframe tasks, create subtasks (one per day)
        if task_type == 'timeframe' and task.timeframe_days:
            start = task.timeframe_start_date
            for day_num in range(task.timeframe_days):
                date = start + timedelta(days=day_num)
                Task.objects.create(
                    user=task.user,
                    title=f"{task.title} - Day {day_num + 1}",
                    description=task.description,
                    task_type='timeframe',
                    priority=task.priority,
                    status=Task.Status.TODO,
                    tags=task.tags,
                    category=task.category,
                    color=task.color,
                    parent_task=task,
                    xp_reward=10,
                    penalty_points=task.penalty_points,
                    original_date=date,
                    start_time=timezone.make_aware(
                        timezone.datetime.combine(date, user.day_start_time)
                    ),
                    end_time=timezone.make_aware(
                        timezone.datetime.combine(date, user.day_end_time)
                    ),
                )

        return task


class TaskListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    pending_subtasks_count = serializers.ReadOnlyField()
    total_subtasks_count = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'task_type', 'priority', 'status', 'category', 'color',
            'start_time', 'end_time', 'is_recurring', 'recurrence_type',
            'xp_reward', 'completion_percentage', 'is_overdue', 'tags',
            'timeframe_days', 'timeframe_start_date', 'timeframe_end_date',
            'pending_subtasks_count', 'total_subtasks_count',
            'parent_task', 'is_rolled_over', 'rollover_count',
        )
