from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import uuid

class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PUBLISHED, 'Опубликовано'),
        (STATUS_ARCHIVED, 'Архив'),
    ]

    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Slug', max_length=255, unique=True, blank=True)
    short_description = models.TextField('Краткое описание', max_length=500)
    content = models.TextField('Полный текст')
    image = models.ImageField('Изображение', upload_to='blog/', blank=True, null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    # ПРАВИЛЬНОЕ ПОЛЕ STATUS
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED
    )
    
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        blank=True,
        verbose_name='Лайки'
    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            self.STATUS_DRAFT: '#8b909a',
            self.STATUS_PUBLISHED: '#22c55e',
            self.STATUS_ARCHIVED: '#f5c842',
        }
        return colors.get(self.status, '#8b909a')