from django.db import models
from users.models import CustomUser

class Animal(models.Model):
    STATUS_CHOICES = [
        ('in_shelter', 'В приюте'),
        ('adopted', 'Усыновлено')
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # кошка, собака и т.д.
    breed = models.CharField(max_length=100, blank=True, null=True)  # порода, необязательное поле
    age_years = models.PositiveIntegerField(default=0)  # годы
    age_months = models.PositiveIntegerField(default=0)  # месяцы
    health_status = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_shelter')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.species})"

    def full_age(self):
        """Возвращает возраст в формате '1 год 6 месяцев'"""
        parts = []
        if self.age_years:
            parts.append(f"{self.age_years} год{'а' if self.age_years == 1 else 'ов'}")
        if self.age_months:
            parts.append(f"{self.age_months} мес.")
        return ' '.join(parts) or "Возраст не указан"


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, related_name='photos', on_delete=models.CASCADE)
    photo_url = models.ImageField(upload_to='animals/%Y/%m/%d')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото {self.animal.name} ({self.id})"