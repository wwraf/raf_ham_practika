from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Task


# ─── РЕГИСТРАЦИЯ ──────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, required=True,
                                      validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True,
                                      label='Подтверждение пароля')

    class Meta:
        model  = User
        fields = ('username', 'email', 'password', 'password2',
                  'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# ─── ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


# ─── ЗАДАЧА ──────────────────────────────────────────────────────────────────

class TaskSerializer(serializers.ModelSerializer):
    # owner показывается как read-only — нельзя изменить через API
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Task
        fields = (
            'id', 'title', 'description',
            'status', 'priority',
            'created_at', 'updated_at',
            'owner',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')

    def validate_status(self, value):
        valid = [s[0] for s in Task.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(
                f'Недопустимый статус. Допустимые: {valid}'
            )
        return value

    def validate_priority(self, value):
        valid = [p[0] for p in Task.PRIORITY_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(
                f'Недопустимый приоритет. Допустимые: {valid}'
            )
        return value