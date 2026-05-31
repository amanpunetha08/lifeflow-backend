from rest_framework import viewsets
from rest_framework.response import Response
from .models import Achievement, UserAchievement, XPLog, StreakRecord, DailyChallenge, UserDailyChallenge
from .serializers import (
    UserAchievementSerializer, XPLogSerializer,
    StreakRecordSerializer, DailyChallengeSerializer, UserDailyChallengeSerializer,
)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()

    def list(self, request):
        user = request.user
        achievements = Achievement.objects.all()
        user_achievements = {ua.achievement_id: ua for ua in UserAchievement.objects.filter(user=user)}

        result = []
        for a in achievements:
            ua = user_achievements.get(a.id)
            progress = 0
            if a.requirement_type == "streak":
                progress = user.streak_count
            elif a.requirement_type == "tasks_completed":
                progress = user.total_completed_tasks
            elif a.requirement_type == "level":
                progress = user.level
            elif a.requirement_type == "xp":
                progress = user.total_xp

            result.append({
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "requirement_type": a.requirement_type,
                "requirement_value": a.requirement_value,
                "progress": min(progress, a.requirement_value),
                "unlocked": ua is not None,
                "unlocked_at": ua.unlocked_at.isoformat() if ua else None,
            })
        return Response(result)

    def retrieve(self, request, pk=None):
        return self.list(request)


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
