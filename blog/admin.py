from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'likes_count')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'short_description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Контент', {
            'fields': ('short_description', 'content', 'image')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at', 'likes_count'),
            'classes': ('collapse',),
        }),
    )

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Лайков'