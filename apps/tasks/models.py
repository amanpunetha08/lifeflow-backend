from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Tag(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#6366f1")

    class Meta:
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    class TaskType(models.TextChoices):
        DAILY = "daily"
        TIMEFRAME = "timeframe"

    class Priority(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        URGENT = "urgent"

    class Status(models.TextChoices):
        TODO = "todo"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        MISSED = "missed"

    class RecurrenceType(models.TextChoices):
        NONE = "none"
        DAILY = "daily"
        WEEKDAYS = "weekdays"
        WEEKLY = "weekly"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.DAILY)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    tags = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default="#6366f1")

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.PositiveIntegerField(null=True, blank=True)
    actual_duration = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    recurrence_type = models.CharField(max_length=10, choices=RecurrenceType.choices, default=RecurrenceType.NONE)
    is_recurring = models.BooleanField(default=False)
    parent_task = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks")

    xp_reward = models.PositiveIntegerField(default=10)
    penalty_points = models.PositiveIntegerField(default=5)
    completion_percentage = models.PositiveIntegerField(default=0)

    is_rolled_over = models.BooleanField(default=False)
    rollover_count = models.PositiveIntegerField(default=0)
    original_date = models.DateField(null=True, blank=True)

    timeframe_days = models.PositiveIntegerField(null=True, blank=True)
    timeframe_start_date = models.DateField(null=True, blank=True)
    timeframe_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
