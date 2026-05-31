from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class ScheduledEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        GENERATED = "generated"
        COMPLETED = "completed"
        MISSED = "missed"
        ROLLED_OVER = "rolled_over"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scheduled_events")
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    details = models.JSONField(default=dict, blank=True)
