from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    xp_for_next_level = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'display_name', 'profile_image',
            'onboarding_completed', 'day_start_time', 'day_end_time',
            'level', 'xp', 'total_xp', 'xp_for_next_level',
            'streak_count', 'longest_streak', 'discipline_score',
            'coins', 'total_completed_tasks', 'chaos_meter',
            'date_joined',
        )
        read_only_fields = ('id', 'date_joined')
