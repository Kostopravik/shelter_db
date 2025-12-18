from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAndUsersTests(TestCase):
    """Тесты регистрации, аутентификации и прав доступа к API пользователей."""

    def setUp(self):
        """Создаём базового администратора и обычного пользователя."""
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass",
            role="admin",
        )
        self.user = User.objects.create_user(
            username="user",
            password="userpass",
            role="adopter",
        )

    def test_register_creates_adopter_and_logs_in(self):
        """Регистрация через форму создаёт пользователя с ролью adopter и сразу авторизует его."""
        url = reverse("register")
        response = self.client.post(
            url,
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        new_user = User.objects.get(username="newuser")
        self.assertEqual(new_user.role, "adopter")
        # Проверяем, что пользователь авторизован (в шаблоне будет доступен user.is_authenticated)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_view_authenticates_user(self):
        """Логин через форму аутентифицирует пользователя и делает редирект на главную."""
        url = reverse("login")
        response = self.client.post(
            url,
            data={"username": "user", "password": "userpass"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_logout_view_logs_out_user(self):
        """Выход из системы разлогинивает пользователя."""
        self.client.login(username="user", password="userpass")
        url = reverse("logout")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_user_list_api_admin_sees_all_users(self):
        """Администратор через API /users/api/users/ видит всех пользователей."""
        self.client.login(username="admin", password="adminpass")
        url = reverse("api_users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_user_list_api_non_admin_sees_only_self(self):
        """Обычный пользователь через API /users/api/users/ видит только себя."""
        self.client.login(username="user", password="userpass")
        url = reverse("api_users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["username"], "user")

    def test_create_user_via_api_forbidden_for_non_admin(self):
        """Создание пользователей через API запрещено для не‑админов (ожидаем статус 403)."""
        self.client.login(username="user", password="userpass")
        url = reverse("api_users")
        response = self.client.post(
            url,
            data={
                "username": "apiuser",
                "password": "SomePass123!",
                "email": "api@example.com",
                "role": "adopter",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username="apiuser").exists())

