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

    user = models.ForeignKey(CustomUser, related_name='adoptions', on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, related_name='adoptions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField()  # обязательно

    class Meta:
        unique_together = ('user', 'animal')

    def __str__(self):
        return f"Заявка: {self.user.username} → {self.animal.name} ({self.status})"


class Return(models.Model):
    adoption = models.OneToOneField(Adoption, related_name='return_record', on_delete=models.CASCADE)
    reason = models.TextField()  # обязательно
    returned_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(CustomUser, related_name='processed_returns', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Возврат {self.adoption.animal.name} ({self.returned_at.date()})"
