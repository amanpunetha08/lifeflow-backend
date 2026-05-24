from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)
    day_start_time = models.TimeField(default='09:00:00')
    day_end_time = models.TimeField(default='23:00:00')
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    streak_count = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    discipline_score = models.FloatField(default=50.0)
    coins = models.PositiveIntegerField(default=0)
    total_completed_tasks = models.PositiveIntegerField(default=0)
    chaos_meter = models.FloatField(default=0.0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def xp_for_next_level(self):
        return self.level * 100

    def add_xp(self, amount):
        self.xp += amount
        self.total_xp += amount
        while self.xp >= self.xp_for_next_level:
            self.xp -= self.xp_for_next_level
            self.level += 1
        self.save()
