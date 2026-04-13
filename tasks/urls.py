from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    TaskListCreateView, TaskDetailView,
)

urlpatterns = [
    # Аутентификация
    path('auth/register/', RegisterView.as_view(),  name='register'),
    path('auth/login/',    LoginView.as_view(),     name='login'),
    path('auth/logout/',   LogoutView.as_view(),    name='logout'),
    path('auth/me/',       ProfileView.as_view(),   name='profile'),

    # Задачи
    path('tasks/',         TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(),    name='task-detail'),
]