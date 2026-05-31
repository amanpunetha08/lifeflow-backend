from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AchievementViewSet, UserAchievementViewSet, XPLogViewSet,
    StreakRecordViewSet, DailyChallengeViewSet, UserDailyChallengeViewSet,
)

router = DefaultRouter()
router.register(r"achievements", AchievementViewSet, basename="achievement")
router.register(r"user-achievements", UserAchievementViewSet, basename="user-achievement")
router.register(r"xp-logs", XPLogViewSet, basename="xp-log")
router.register(r"streaks", StreakRecordViewSet, basename="streak")
router.register(r"challenges", DailyChallengeViewSet, basename="challenge")
router.register(r"user-challenges", UserDailyChallengeViewSet, basename="user-challenge")

urlpatterns = [
    path("", include(router.urls)),
]
