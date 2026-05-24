from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Tag
from .serializers import TaskSerializer, TaskListSerializer, TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'category', 'is_recurring', 'recurrence_type', 'task_type']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.COMPLETED
        task.completed_at = timezone.now()
        task.completion_percentage = 100.0
        if task.start_time and task.completed_at:
            task.actual_duration = int((task.completed_at - task.start_time).total_seconds() / 60)
        task.save()

        # Award XP
        user = request.user
        user.add_xp(task.xp_reward)
        user.total_completed_tasks += 1
        user.coins += 1
        user.save()

        # If all subtasks of parent are completed, mark parent completed
        if task.parent_task:
            parent = task.parent_task
            if parent.subtasks.exclude(status=Task.Status.COMPLETED).count() == 0:
                parent.status = Task.Status.COMPLETED
                parent.completed_at = timezone.now()
                parent.completion_percentage = 100.0
                parent.save()

        return Response(TaskSerializer(task).data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        # Show: today's tasks (daily + subtasks scheduled for today + piled-up subtasks)
        tasks = self.get_queryset().filter(
            Q(start_time__date=today, status__in=['todo', 'in_progress', 'completed']) |
            Q(parent_task__isnull=False, status__in=['todo', 'in_progress'], start_time__date__lte=today)
        ).exclude(status='missed').distinct()
        return Response(TaskListSerializer(tasks, many=True).data)

    @action(detail=False, methods=['get'])
    def missed(self, request):
        tasks = self.get_queryset().filter(status=Task.Status.MISSED)
        return Response(TaskListSerializer(tasks, many=True).data)
