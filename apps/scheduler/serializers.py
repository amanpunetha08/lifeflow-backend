from rest_framework import serializers
from .models import RecurringRule, ScheduledEvent
from apps.tasks.serializers import TaskListSerializer


class RecurringRuleSerializer(serializers.ModelSerializer):
    task_template_detail = TaskListSerializer(source='task_template', read_only=True)

    class Meta:
        model = RecurringRule
        fields = ('id', 'task_template', 'task_template_detail', 'is_active', 'days_of_week', 'start_date', 'end_date', 'last_generated')
        read_only_fields = ('last_generated',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ScheduledEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledEvent
        fields = ('id', 'task', 'event_type', 'details', 'created_at')
