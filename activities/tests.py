from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ActivitiesPermissionsTests(TestCase):
    """Тесты прав доступа к созданию активностей через шаблон и API."""

    def setUp(self):
        """Создаём пользователя‑волонтёра и обычного усыновителя."""
        self.client = Client()
        self.volunteer = User.objects.create_user(
            username="volunteer",
            password="volpass",
            role="volunteer",
        )
        self.adopter = User.objects.create_user(
            username="adopter",
            password="adopterpass",
            role="adopter",
        )

    def test_adopter_cannot_create_activity_via_template_view(self):
        """Обычный пользователь не может создать новость через веб‑форму (редирект с ошибкой)."""
        self.client.login(username="adopter", password="adopterpass")
        url = reverse("create_activity")
        response = self.client.post(
            url,
            data={
                "title": "Новость",
                "description": "Описание",
                "activity_type": "news",
            },
            follow=True,
        )
        # Должно выполниться перенаправление (нет прав -> редирект на home)
        self.assertEqual(response.status_code, 200)
        # На странице должно быть сообщение об ошибке прав
        messages = list(response.context["messages"])
        self.assertTrue(any("Только администраторы и волонтёры" in str(m) for m in messages))

    def test_volunteer_can_create_activity_via_api(self):
        """Волонтёр может создать активность через API (ожидаем 201)."""
        self.client.login(username="volunteer", password="volpass")
        url = reverse("api_activities")
        response = self.client.post(
            url,
            data={
                "title": "API‑новость",
                "description": "Описание",
                "activity_type": "news",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

