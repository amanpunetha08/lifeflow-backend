from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Tag(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6366f1')

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        MISSED = 'missed', 'Missed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    class TaskType(models.TextChoices):
        DAILY = 'daily', 'Daily'
        TIMEFRAME = 'timeframe', 'Timeframe'

    class RecurrenceType(models.TextChoices):
        NONE = 'none', 'None'
        DAILY = 'daily', 'Daily'
        WEEKDAYS = 'weekdays', 'Weekdays'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=10, choices=TaskType.choices, default=TaskType.DAILY)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.TODO)
    tags = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=7, default='#6366f1')
    icon = models.CharField(max_length=50, blank=True)

    # Scheduling
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.PositiveIntegerField(help_text='Duration in minutes', null=True, blank=True)
    actual_duration = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Timeframe task fields
    timeframe_days = models.PositiveIntegerField(null=True, blank=True, help_text='Number of days to complete this task')
    timeframe_start_date = models.DateField(null=True, blank=True)
    timeframe_end_date = models.DateField(null=True, blank=True)

    # Recurrence
    recurrence_type = models.CharField(max_length=10, choices=RecurrenceType.choices, default=RecurrenceType.NONE)
    is_recurring = models.BooleanField(default=False)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subtasks')

    # Gamification
    xp_reward = models.PositiveIntegerField(default=10)
    penalty_points = models.PositiveIntegerField(default=5)
    completion_percentage = models.FloatField(default=0.0)

    # Rollover tracking
    is_rolled_over = models.BooleanField(default=False)
    rollover_count = models.PositiveIntegerField(default=0)
    original_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.end_time and self.status not in (self.Status.COMPLETED, self.Status.MISSED):
            return timezone.now() > self.end_time
        return False

    @property
    def pending_subtasks_count(self):
        return self.subtasks.exclude(status=self.Status.COMPLETED).count()

    @property
    def total_subtasks_count(self):
        return self.subtasks.count()
