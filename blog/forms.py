from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'short_description', 'content', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите заголовок публикации...',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Краткое описание (до 500 символов)...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 10,
                'placeholder': 'Полный текст публикации...',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-input-file',
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
            }),
        }
        labels = {
            'title': 'Заголовок',
            'short_description': 'Краткое описание',
            'content': 'Полный текст',
            'image': 'Изображение',
            'status': 'Статус публикации',
        }