from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('catalog.urls')),
    path('blog/', include('blog.urls', namespace='blog')),

    # 👇 добавляем API
    path('api/', include('tasks.urls')),
]