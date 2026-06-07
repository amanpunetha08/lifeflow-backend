from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ScheduledEvent
from .serializers import ScheduledEventSerializer
from .services import process_expired_tasks, seed_2week_plan


class SchedulerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduledEventSerializer

    def get_queryset(self):
        return ScheduledEvent.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["post"])
    def process_expired(self, request):
        result = process_expired_tasks(request.user)
        return Response(result)

    @action(detail=False, methods=["post"])
    def seed_plan(self, request):
        result = seed_2week_plan(request.user)
        return Response(result)
