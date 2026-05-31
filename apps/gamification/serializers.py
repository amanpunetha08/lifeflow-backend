from rest_framework import serializers
from .models import Achievement, UserAchievement, XPLog, StreakRecord, DailyChallenge, UserDailyChallenge


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = "__all__"


class XPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPLog
        fields = "__all__"


class StreakRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakRecord
        fields = "__all__"


class DailyChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyChallenge
        fields = "__all__"


class UserDailyChallengeSerializer(serializers.ModelSerializer):
    challenge = DailyChallengeSerializer(read_only=True)

    class Meta:
        model = UserDailyChallenge
        fields = "__all__"
