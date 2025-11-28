from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Роли пользователей
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('volunteer', 'Volunteer'),
        ('adopter', 'Adopter')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='adopter')

    # Анкета усыновителя (только для adopter)
    has_experience = models.BooleanField(default=False)
    has_other_pets = models.BooleanField(default=False)
    ready_for_pet = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)

    # Дата регистрации автоматически
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
