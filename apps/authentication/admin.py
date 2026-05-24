from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'level', 'xp', 'streak_count', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Gamification', {'fields': ('profile_image', 'level', 'xp', 'total_xp', 'streak_count', 'longest_streak', 'discipline_score', 'coins', 'total_completed_tasks', 'chaos_meter')}),
    )
