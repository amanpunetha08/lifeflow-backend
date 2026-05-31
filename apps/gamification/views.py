from rest_framework import viewsets, mixins
from .models import Achievement, UserAchievement, XPLog, StreakRecord, DailyChallenge, UserDailyChallenge
from .serializers import (
    AchievementSerializer, UserAchievementSerializer, XPLogSerializer,
    StreakRecordSerializer, DailyChallengeSerializer, UserDailyChallengeSerializer,
)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)


class XPLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = XPLogSerializer

    def get_queryset(self):
        return XPLog.objects.filter(user=self.request.user).order_by("-created_at")


class StreakRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StreakRecordSerializer

    def get_queryset(self):
        return StreakRecord.objects.filter(user=self.request.user).order_by("-date")


class DailyChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyChallenge.objects.all()
    serializer_class = DailyChallengeSerializer


class UserDailyChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserDailyChallengeSerializer

    def get_queryset(self):
        return UserDailyChallenge.objects.filter(user=self.request.user)
