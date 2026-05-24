from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RecurringRule, ScheduledEvent
from .serializers import RecurringRuleSerializer, ScheduledEventSerializer
from .services import generate_daily_tasks, process_expired_tasks


class RecurringRuleViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringRuleSerializer

    def get_queryset(self):
        return RecurringRule.objects.filter(user=self.request.user).select_related('task_template')

    @action(detail=False, methods=['post'])
    def trigger_generation(self, request):
        """Manually trigger daily task generation (for testing)."""
        generate_daily_tasks()
        return Response({'status': 'Daily tasks generated'})

    @action(detail=False, methods=['post'])
    def process_expired(self, request):
        """Manually trigger expired task processing (for testing)."""
        process_expired_tasks()
        return Response({'status': 'Expired tasks processed'})


class ScheduledEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ScheduledEventSerializer

    def get_queryset(self):
        return ScheduledEvent.objects.filter(user=self.request.user)
