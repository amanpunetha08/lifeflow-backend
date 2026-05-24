from django.contrib import admin
from .models import RecurringRule, ScheduledEvent

@admin.register(RecurringRule)
class RecurringRuleAdmin(admin.ModelAdmin):
    list_display = ('task_template', 'user', 'is_active', 'start_date', 'last_generated')

@admin.register(ScheduledEvent)
class ScheduledEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'event_type', 'created_at')
    list_filter = ('event_type',)
