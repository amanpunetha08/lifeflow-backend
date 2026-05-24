from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class RecurringRule(TimeStampedModel):
    """Defines a recurring task template that generates daily instances."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_rules')
    task_template = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='recurring_rule')
    is_active = models.BooleanField(default=True)
    days_of_week = models.JSONField(default=list, blank=True, help_text='[0=Mon, 6=Sun]')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    last_generated = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Rule: {self.task_template.title} ({self.get_recurrence_display()})"

    def get_recurrence_display(self):
        return self.task_template.get_recurrence_type_display()


class ScheduledEvent(TimeStampedModel):
    """Tracks task lifecycle events for analytics and penalty/reward processing."""
    class EventType(models.TextChoices):
        GENERATED = 'generated', 'Generated'
        COMPLETED = 'completed', 'Completed'
        MISSED = 'missed', 'Missed'
        ROLLED_OVER = 'rolled_over', 'Rolled Over'
        PENALTY_APPLIED = 'penalty_applied', 'Penalty Applied'
        XP_AWARDED = 'xp_awarded', 'XP Awarded'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_events')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
