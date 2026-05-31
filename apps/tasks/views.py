import zoneinfo
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer

IST = zoneinfo.ZoneInfo("Asia/Kolkata")


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "completed"
        task.completed_at = timezone.now()
        task.completion_percentage = 100
        task.save()
        user = request.user
        user.add_xp(task.xp_reward)
        user.coins += max(1, task.xp_reward // 2)
        user.total_completed_tasks += 1
        user.discipline_score = min(100, user.discipline_score + 1)
        user.chaos_meter = max(0, user.chaos_meter - 1)
        user.save()
        return Response(TaskSerializer(task).data)

    @action(detail=False, methods=["get"])
    def today(self, request):
        today = timezone.now().astimezone(IST).date()
        timezone.activate(IST)
        tasks = self.get_queryset().filter(start_time__date=today).exclude(status='missed')
        timezone.deactivate()
        return Response(TaskSerializer(tasks, many=True).data)

    @action(detail=False, methods=["get"])
    def missed(self, request):
        tasks = self.get_queryset().filter(status="missed")
        return Response(TaskSerializer(tasks, many=True).data)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
