from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, XPLogViewSet, StreakViewSet, DailyChallengeViewSet

router = DefaultRouter()
router.register('achievements', AchievementViewSet, basename='achievement')
router.register('xp-logs', XPLogViewSet, basename='xp-log')
router.register('streaks', StreakViewSet, basename='streak')
router.register('challenges', DailyChallengeViewSet, basename='daily-challenge')

urlpatterns = [
    path('', include(router.urls)),
]
