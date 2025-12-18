from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from animals.models import Animal
from .models import Adoption, Return

User = get_user_model()


class AdoptionPermissionsTests(TestCase):
    """Тесты прав доступа и ролей для заявок на усыновление и возвратов."""

    def setUp(self):
        """Создаём базовых пользователей и животное для тестов."""
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
        self.other_adopter = User.objects.create_user(
            username="other",
            password="otherpass",
            role="adopter",
        )

        self.animal = Animal.objects.create(
            name="Барсик",
            species="Кот",
            breed="",
            age_years=2,
            age_months=0,
            health_status="Здоров",
            status="in_shelter",
        )

        self.adoption = Adoption.objects.create(
            user=self.adopter,
            animal=self.animal,
            status="pending",
            rejection_reason="",
        )

    def test_volunteer_cannot_approve_adoption_via_api(self):
        """Волонтёр не может менять статус заявки через API (должен вернуться 403)."""
        self.client.login(username="volunteer", password="volpass")
        url = reverse("api_adoption_detail", args=[self.adoption.id])
        response = self.client.put(
            url,
            data={"status": "approved"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.adoption.refresh_from_db()
        self.assertEqual(self.adoption.status, "pending")

    def test_admin_can_approve_adoption_via_api(self):
        """Администратор может одобрить заявку через API и обновить статус животного."""
        self.client.login(username="admin", password="adminpass")
        url = reverse("api_adoption_detail", args=[self.adoption.id])
        response = self.client.put(
            url,
            data={"status": "approved"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.adoption.refresh_from_db()
        self.animal.refresh_from_db()
        self.assertEqual(self.adoption.status, "approved")
        self.assertEqual(self.animal.status, "adopted")

    def test_return_requires_reason_in_return_list_view(self):
        """При оформлении возврата через страницу возвратов обязательно указывать причину."""
        # Делаем заявку одобренной
        self.adoption.status = "approved"
        self.adoption.save()

        self.client.login(username="adopter", password="adopterpass")
        url = reverse("return_list")
        response = self.client.post(
            url,
            data={"adoption_id": self.adoption.id, "reason": ""},
            follow=True,
        )
        # Возврат не должен быть создан
        self.assertEqual(Return.objects.count(), 0)
        # На странице должно присутствовать сообщение об ошибке
        messages = list(response.context["messages"])
        self.assertTrue(any("Необходимо указать причину возврата" in str(m) for m in messages))

    def test_only_owner_can_create_return(self):
        """Пользователь не может оформить возврат по чужой заявке (даже если он админ/волонтёр)."""
        # Делаем заявку одобренной
        self.adoption.status = "approved"
        self.adoption.save()

        # Пытаемся оформить возврат другим усыновителем
        self.client.login(username="other", password="otherpass")
        url = reverse("return_list")
        self.client.post(
            url,
            data={"adoption_id": self.adoption.id, "reason": "Хочу вернуть"},
            follow=True,
        )
        self.assertEqual(Return.objects.count(), 0)

        # Пытаемся оформить возврат администратором
        self.client.login(username="admin", password="adminpass")
        self.client.post(
            url,
            data={"adoption_id": self.adoption.id, "reason": "Админ не должен так делать"},
            follow=True,
        )
        self.assertEqual(Return.objects.count(), 0)

    def test_owner_can_create_return_and_statuses_change(self):
        """Владелец заявки может оформить возврат: создаётся запись, статусы меняются, выводится сообщение с телефоном."""
        self.adoption.status = "approved"
        self.adoption.save()

        self.client.login(username="adopter", password="adopterpass")
        url = reverse("return_list")
        response = self.client.post(
            url,
            data={"adoption_id": self.adoption.id, "reason": "Аллергия у ребёнка"},
            follow=True,
        )

        self.assertEqual(Return.objects.count(), 1)
        return_obj = Return.objects.first()
        self.assertEqual(return_obj.adoption, self.adoption)
        self.assertEqual(return_obj.reason, "Аллергия у ребёнка")

        self.adoption.refresh_from_db()
        self.animal.refresh_from_db()
        self.assertEqual(self.adoption.status, "returned")
        self.assertEqual(self.animal.status, "in_shelter")

        messages = list(response.context["messages"])
        self.assertTrue(any("+7 000 0000 0000" in str(m) for m in messages))

