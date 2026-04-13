from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from .models import Task


class AuthTests(APITestCase):
    """Тесты регистрации и входа."""

    def test_register_success(self):
        """Успешная регистрация нового пользователя."""
        url  = reverse('register')
        data = {
            'username':  'testuser',
            'email':     'test@example.com',
            'password':  'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_password_mismatch(self):
        """Регистрация с несовпадающими паролями должна вернуть 400."""
        url  = reverse('register')
        data = {
            'username':  'testuser2',
            'password':  'StrongPass123!',
            'password2': 'WrongPass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Успешный вход зарегистрированного пользователя."""
        User.objects.create_user(username='loginuser', password='Pass1234!')
        url      = reverse('login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'Pass1234!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        """Вход с неверным паролем должен вернуть 400."""
        User.objects.create_user(username='loginuser2', password='Pass1234!')
        url      = reverse('login')
        response = self.client.post(url, {'username': 'loginuser2', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Выход удаляет токен."""
        user  = User.objects.create_user(username='logoutuser', password='Pass1234!')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=user).exists())


class TaskTests(APITestCase):
    """Тесты CRUD задач."""

    def setUp(self):
        # Основной пользователь
        self.user  = User.objects.create_user(username='owner', password='Pass1234!')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Другой пользователь
        self.other_user  = User.objects.create_user(username='other', password='Pass1234!')
        self.other_token = Token.objects.create(user=self.other_user)

        # Задача другого пользователя
        self.other_task = Task.objects.create(
            title='Чужая задача',
            owner=self.other_user,
        )

    def test_create_task(self):
        """Авторизованный пользователь может создать задачу."""
        url  = reverse('task-list')
        data = {'title': 'Моя задача', 'description': 'Описание', 'priority': 'high'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Моя задача')
        self.assertEqual(response.data['owner'], 'owner')

    def test_create_task_unauthenticated(self):
        """Неавторизованный пользователь не может создать задачу."""
        self.client.credentials()   # сбрасываем токен
        url      = reverse('task-list')
        response = self.client.post(url, {'title': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tasks_only_own(self):
        """Пользователь видит только свои задачи."""
        Task.objects.create(title='Моя 1', owner=self.user)
        Task.objects.create(title='Моя 2', owner=self.user)
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В results только задачи текущего пользователя
        results = response.data.get('results', response.data)
        for task in results:
            self.assertEqual(task['owner'], 'owner')

    def test_retrieve_own_task(self):
        """Пользователь может просмотреть свою задачу."""
        task     = Task.objects.create(title='Моя задача', owner=self.user)
        response = self.client.get(reverse('task-detail', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Моя задача')

    def test_access_other_user_task_forbidden(self):
        """Запрет доступа к чужой задаче — должен вернуть 404."""
        response = self.client.get(reverse('task-detail', args=[self.other_task.id]))
        # get_queryset фильтрует по owner, поэтому 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_task(self):
        """Пользователь может обновить свою задачу."""
        task     = Task.objects.create(title='Старое', owner=self.user)
        response = self.client.patch(
            reverse('task-detail', args=[task.id]),
            {'title': 'Новое', 'status': 'in_progress'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Новое')
        self.assertEqual(response.data['status'], 'in_progress')

    def test_update_other_user_task_forbidden(self):
        """Обновление чужой задачи запрещено — 404."""
        response = self.client.patch(
            reverse('task-detail', args=[self.other_task.id]),
            {'title': 'Взлом'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_task(self):
        """Пользователь может удалить свою задачу."""
        task     = Task.objects.create(title='Удалить', owner=self.user)
        response = self.client.delete(reverse('task-detail', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_delete_other_user_task_forbidden(self):
        """Удаление чужой задачи запрещено — 404."""
        response = self.client.delete(
            reverse('task-detail', args=[self.other_task.id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_status(self):
        """Фильтрация задач по статусу."""
        Task.objects.create(title='Новая',    owner=self.user, status='new')
        Task.objects.create(title='В работе', owner=self.user, status='in_progress')
        response = self.client.get(reverse('task-list') + '?status=new')
        results  = response.data.get('results', response.data)
        for task in results:
            self.assertEqual(task['status'], 'new')

    def test_owner_field_is_readonly(self):
        """Нельзя изменить owner через API."""
        task = Task.objects.create(title='Задача', owner=self.user)
        response = self.client.patch(
            reverse('task-detail', args=[task.id]),
            {'owner': self.other_user.id},
        )
        task.refresh_from_db()
        self.assertEqual(task.owner, self.user)   # owner не изменился