from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Achievement, UserAchievement, XPLog, StreakRecord, UserDailyChallenge
from .serializers import (
    AchievementSerializer, UserAchievementSerializer,
    XPLogSerializer, StreakRecordSerializer, UserDailyChallengeSerializer,
)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @action(detail=False)
    def mine(self, request):
        user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
        return Response(UserAchievementSerializer(user_achievements, many=True).data)


class XPLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = XPLogSerializer

    def get_queryset(self):
        return XPLog.objects.filter(user=self.request.user)


class StreakViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = StreakRecordSerializer

    def get_queryset(self):
        return StreakRecord.objects.filter(user=self.request.user)

    @action(detail=False)
    def current(self, request):
        today = timezone.now().date()
        records = StreakRecord.objects.filter(user=request.user, date__lte=today).order_by('-date')[:30]
        return Response(StreakRecordSerializer(records, many=True).data)


class DailyChallengeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserDailyChallengeSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return UserDailyChallenge.objects.filter(
            user=self.request.user, challenge__date=today
        ).select_related('challenge')
