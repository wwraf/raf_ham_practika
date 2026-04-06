from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # 1. Сначала статические пути (фиксированные слова)
    path('', views.post_list, name='post_list'),
    path('create/', views.post_create, name='post_create'),
    path('my/posts/', views.my_posts, name='my_posts'),

    # 2. Затем пути с переменными (slug, id и т.д.)
    path('<str:slug>/', views.post_detail, name='post_detail'),
    
    # 3. CRUD и API для конкретных постов
    path('<str:slug>/edit/', views.post_edit, name='post_edit'),
    path('<str:slug>/delete/', views.post_delete, name='post_delete'),
    path('<str:slug>/like/', views.post_like, name='post_like'),
    path('<str:slug>/status/', views.post_change_status, name='post_change_status'),
]