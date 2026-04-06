import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post
from .forms import PostForm

# ─── СПИСОК ПУБЛИКАЦИЙ ───────────────────────────────────────────────────────

def post_list(request):
    """Все публикации: опубликованные доступны всем, черновики — только авторам."""
    q = request.GET.get('q', '').strip()
    
    # Логика фильтрации: Опубликовано ИЛИ (Авторизован И Автор)
    if request.user.is_authenticated:
        posts_query = Post.objects.filter(
            Q(status=Post.STATUS_PUBLISHED) | Q(author=request.user)
        )
    else:
        posts_query = Post.objects.filter(status=Post.STATUS_PUBLISHED)

    # Поиск
    if q:
        posts_query = posts_query.filter(
            Q(title__icontains=q) | Q(short_description__icontains=q)
        )
    
    # Оптимизация и сортировка
    posts_query = posts_query.select_related('author').order_by('-created_at')

    # Пагинация
    paginator = Paginator(posts_query, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ВАЖНО: Возвращаем HttpResponse
    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'q': q,
    })


# ─── ДЕТАЛЬНАЯ СТРАНИЦА ───────────────────────────────────────────────────────

def post_detail(request, slug):
    """Просмотр статьи. Проверка доступа к черновикам."""
    post = get_object_or_404(Post, slug=slug)

    # Если пост не опубликован — проверяем права
    if post.status != Post.STATUS_PUBLISHED:
        if not request.user.is_authenticated:
            return redirect('blog:post_list')
        if request.user != post.author and not request.user.has_perm('blog.change_post'):
            messages.warning(request, "У вас нет доступа к этой черновой публикации.")
            return redirect('blog:post_list')

    user_liked = (
        request.user.is_authenticated
        and post.likes.filter(pk=request.user.pk).exists()
    )

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'user_liked': user_liked,
    })


# ─── СОЗДАНИЕ ────────────────────────────────────────────────────────────────

@login_required
@permission_required('blog.add_post', raise_exception=True)
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация успешно создана!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'Создать публикацию',
        'is_create': True,
    })


# ─── РЕДАКТИРОВАНИЕ ──────────────────────────────────────────────────────────

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Редактировать может автор или тот, у кого есть спец. право
    if post.author != request.user and not request.user.has_perm('blog.change_post'):
        messages.error(request, "Вы не можете редактировать чужую публикацию.")
        return redirect('blog:post_detail', slug=post.slug)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Публикация обновлена!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'action': 'Редактировать публикацию',
        'is_create': False,
    })


# ─── УДАЛЕНИЕ ────────────────────────────────────────────────────────────────

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.has_perm('blog.delete_post'):
        messages.error(request, "У вас нет прав на удаление этой публикации.")
        return redirect('blog:post_detail', slug=post.slug)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация удалена.')
        return redirect('blog:post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# ─── FETCH: ЛАЙК ─────────────────────────────────────────────────────────────

@require_POST
@login_required
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes_count})


# ─── FETCH: ИЗМЕНЕНИЕ СТАТУСА ─────────────────────────────────────────────────

@require_POST
@login_required
def post_change_status(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.has_perm('blog.change_post'):
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        valid_statuses = [s[0] for s in Post.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            post.status = new_status
            post.save(update_fields=['status'])
            return JsonResponse({
                'status': post.status,
                'status_label': post.status_label,
                'status_color': post.status_color,
            })
    except:
        pass
    return JsonResponse({'error': 'Ошибка при смене статуса'}, status=400)


# ─── МОИ ПУБЛИКАЦИИ ──────────────────────────────────────────────────────────

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).select_related('author')
    return render(request, 'blog/my_posts.html', {'posts': posts})