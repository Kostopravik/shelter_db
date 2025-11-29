from django.db import models
from users.models import CustomUser
from animals.models import Animal

class Adoption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('returned', 'Возвращено')
    ]

    user = models.ForeignKey(CustomUser, verbose_name="Пользователь", related_name='adoptions', on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, verbose_name="Животное", related_name='adoptions', on_delete=models.CASCADE)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField("Дата подачи заявки", auto_now_add=True)
    rejection_reason = models.TextField("Причина отклонения", blank=False)  # обязательно

    class Meta:
        verbose_name = "Заявка на усыновление"
        verbose_name_plural = "Заявки на усыновление"
        unique_together = ('user', 'animal')

    def __str__(self):
        return f"Заявка: {self.user.username} → {self.animal.name} ({self.status})"


class Return(models.Model):
    adoption = models.OneToOneField(Adoption, verbose_name="Заявка", related_name='return_record', on_delete=models.CASCADE)
    reason = models.TextField("Причина возврата", blank=False)  # обязательно
    returned_at = models.DateTimeField("Дата возврата", auto_now_add=True)
    processed_by = models.ForeignKey(CustomUser, verbose_name="Обработал", related_name='processed_returns', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Возврат животного"
        verbose_name_plural = "Возвраты животных"

    def __str__(self):
        return f"Возврат {self.adoption.animal.name} ({self.returned_at.date()})"
