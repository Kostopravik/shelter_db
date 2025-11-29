from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class CustomUser(AbstractUser):
    # Роли пользователей
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('volunteer', 'Волонтёр'),
        ('adopter', 'Усыновитель')
    ]
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='adopter')

    # Анкета усыновителя (только для adopter)
    has_experience = models.BooleanField("Есть опыт содержания животных", default=False)
    has_other_pets = models.BooleanField("Есть другие питомцы", default=False)
    ready_for_pet = models.CharField("Готовность к питомцу", max_length=255, blank=True, null=True)

    # Уникальный slug для пользователя
    slug = models.SlugField("Ссылка (slug)", max_length=100, unique=True, blank=True)

    # Дата регистрации автоматически
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Автоматически создаём slug из username, если не указан
        if not self.slug:
            base_slug = slugify(self.username)
            slug = base_slug
            counter = 1
            while CustomUser.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
