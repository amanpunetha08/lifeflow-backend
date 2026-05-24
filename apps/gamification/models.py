from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Achievement(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=10)
    requirement_type = models.CharField(max_length=50)  # e.g., 'streak', 'tasks_completed', 'perfect_day'
    requirement_value = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class UserAchievement(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')


class XPLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_logs')
    amount = models.IntegerField()  # Can be negative for penalties
    reason = models.CharField(max_length=255)
    task = models.ForeignKey('tasks.Task', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']


class StreakRecord(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak_records')
    date = models.DateField()
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_total = models.PositiveIntegerField(default=0)
    is_perfect_day = models.BooleanField(default=False)
    xp_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']


class DailyChallenge(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=50)  # 'complete_n', 'before_time', 'no_miss'
    target_value = models.PositiveIntegerField()
    xp_reward = models.PositiveIntegerField(default=25)
    coin_reward = models.PositiveIntegerField(default=5)
    date = models.DateField()

    class Meta:
        ordering = ['-date']


class UserDailyChallenge(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_challenges')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')
