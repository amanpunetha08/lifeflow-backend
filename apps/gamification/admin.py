from django.contrib import admin
from .models import Achievement, UserAchievement, XPLog, StreakRecord, DailyChallenge, UserDailyChallenge

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'requirement_type', 'requirement_value', 'xp_reward')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')

@admin.register(XPLog)
class XPLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created_at')

@admin.register(StreakRecord)
class StreakRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tasks_completed', 'tasks_total', 'is_perfect_day')

@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'target_value', 'date')

@admin.register(UserDailyChallenge)
class UserDailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'progress', 'is_completed')
