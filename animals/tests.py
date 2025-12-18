from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Animal

User = get_user_model()


class AnimalsPermissionsTests(TestCase):
    """Базовые тесты прав доступа к операциям с животными."""

    def setUp(self):
        """Создаём пользователей разных ролей и пример животного."""
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass",
            role="admin",
        )
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
        self.animal = Animal.objects.create(
            name="Шарик",
            species="Собака",
            breed="",
            age_years=3,
            age_months=0,
            health_status="Здоров",
            status="in_shelter",
        )

    def test_adopter_cannot_create_animal_via_api(self):
        """Обычный усыновитель не может добавлять животных через API (ожидаем 403)."""
        self.client.login(username="adopter", password="adopterpass")
        url = reverse("api_animals")
        response = self.client.post(
            url,
            data={
                "name": "Тест",
                "species": "Кот",
                "health_status": "Здоров",
                "status": "in_shelter",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_volunteer_can_create_animal_via_api(self):
        """Волонтёр может добавлять животных через API (ожидаем 201)."""
        self.client.login(username="volunteer", password="volpass")
        url = reverse("api_animals")
        response = self.client.post(
            url,
            data={
                "name": "Новый кот",
                "species": "Кот",
                "health_status": "Здоров",
                "status": "in_shelter",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

