from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)

    # Gamification
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    streak_count = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    discipline_score = models.PositiveIntegerField(default=50)
    coins = models.PositiveIntegerField(default=0)
    total_completed_tasks = models.PositiveIntegerField(default=0)
    chaos_meter = models.PositiveIntegerField(default=0)

    # Preferences
    day_start_time = models.TimeField(default="06:00:00")
    day_end_time = models.TimeField(default="23:00:00")
    onboarding_completed = models.BooleanField(default=False)
    last_processed_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def add_xp(self, amount):
        self.xp += amount
        self.total_xp += amount
        xp_needed = self.level * 100
        while self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            xp_needed = self.level * 100
        self.save()
