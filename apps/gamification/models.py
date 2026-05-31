from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Achievement(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    requirement_type = models.CharField(max_length=50)
    requirement_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "achievement"]


class XPLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_logs")
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    task = models.ForeignKey("tasks.Task", on_delete=models.SET_NULL, null=True, blank=True)


class StreakRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak_records")
    date = models.DateField()
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_total = models.PositiveIntegerField(default=0)
    is_perfect_day = models.BooleanField(default=False)
    xp_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["user", "date"]


class DailyChallenge(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=50)
    target_value = models.PositiveIntegerField(default=1)
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=25)
    date = models.DateField()

    def __str__(self):
        return self.title


class UserDailyChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_challenges")
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "challenge"]
