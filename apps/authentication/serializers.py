from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "username", "password", "display_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "display_name", "profile_image", "bio",
            "level", "xp", "total_xp", "streak_count", "longest_streak",
            "discipline_score", "coins", "total_completed_tasks", "chaos_meter",
            "day_start_time", "day_end_time", "onboarding_completed",
        ]
        read_only_fields = [
            "id", "email", "level", "xp", "total_xp", "streak_count",
            "longest_streak", "coins", "total_completed_tasks",
        ]
