from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    STATUS_NEW         = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE        = 'done'
    STATUS_CHOICES = [
        (STATUS_NEW,         'Новая'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_DONE,        'Выполнена'),
    ]

    PRIORITY_LOW    = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH   = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW,    'Низкий'),
        (PRIORITY_MEDIUM, 'Средний'),
        (PRIORITY_HIGH,   'Высокий'),
    ]

    title       = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Описание', blank=True)
    status      = models.CharField(
        'Статус', max_length=20,
        choices=STATUS_CHOICES, default=STATUS_NEW,
        db_index=True          # индекс для фильтрации
    )
    priority    = models.CharField(
        'Приоритет', max_length=10,
        choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM,
        db_index=True
    )
    created_at  = models.DateTimeField('Создано', auto_now_add=True, db_index=True)
    updated_at  = models.DateTimeField('Обновлено', auto_now=True)
    owner       = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tasks', verbose_name='Владелец'
    )

    class Meta:
        verbose_name        = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering            = ['-created_at']

    def __str__(self):
        return f'[{self.get_priority_display()}] {self.title} ({self.get_status_display()})'