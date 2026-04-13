import logging
from django.contrib.auth.models import User
from rest_framework import generics, status, filters
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Task
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer
from .permissions import IsOwner
from .pagination import TaskPagination

logger = logging.getLogger('tasks')


# ─── РЕГИСТРАЦИЯ ──────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация нового пользователя."""
    queryset         = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f'Новый пользователь зарегистрирован: {user.username}')
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


# ─── ВХОД ─────────────────────────────────────────────────────────────────────

class LoginView(ObtainAuthToken):
    """POST /api/auth/login/ — вход, возвращает токен."""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user  = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f'Пользователь вошёл: {user.username}')
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


# ─── ВЫХОД ────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """POST /api/auth/logout/ — удаление токена (выход)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            logger.info(f'Пользователь вышел: {request.user.username}')
        except Exception:
            pass
        return Response({'detail': 'Вы вышли из системы.'})


# ─── ПРОФИЛЬ ──────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — данные текущего пользователя."""
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── СПИСОК И СОЗДАНИЕ ЗАДАЧ ──────────────────────────────────────────────────

class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/        — список задач текущего пользователя
    POST /api/tasks/        — создание задачи
    Фильтрация: ?status=new&priority=high
    Сортировка: ?ordering=created_at  или  ?ordering=priority
    """
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class   = TaskPagination

    # Фильтрация и сортировка
    filter_backends  = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    ordering_fields  = ['created_at', 'priority', 'status']
    ordering         = ['-created_at']   # сортировка по умолчанию

    def get_queryset(self):
        # Только свои задачи — оптимизация select_related
        return Task.objects.filter(
            owner=self.request.user
        ).select_related('owner')

    def perform_create(self, serializer):
        task = serializer.save(owner=self.request.user)
        logger.info(
            f'Задача создана: id={task.id} title="{task.title}" '
            f'owner={self.request.user.username}'
        )


# ─── ОДНА ЗАДАЧА ──────────────────────────────────────────────────────────────

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/ — просмотр
    PUT    /api/tasks/<id>/ — полное обновление
    PATCH  /api/tasks/<id>/ — частичное обновление
    DELETE /api/tasks/<id>/ — удаление
    """
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user
        ).select_related('owner')

    def perform_destroy(self, instance):
        logger.info(
            f'Задача удалена: id={instance.id} title="{instance.title}" '
            f'owner={self.request.user.username}'
        )
        instance.delete()