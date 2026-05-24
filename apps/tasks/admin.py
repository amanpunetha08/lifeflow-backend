from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'is_recurring', 'xp_reward', 'start_time')
    list_filter = ('status', 'priority', 'is_recurring', 'recurrence_type')
    search_fields = ('title', 'description')
