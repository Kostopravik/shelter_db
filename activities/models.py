from django.db import models
from users.models import CustomUser

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('feeding', 'Кормление'),
        ('medical', 'Медосмотр'),
        ('cleaning', 'Уборка'),
        ('event', 'Мероприятие'),
        ('news', 'Новости'),
        ('advice', 'Совет по уходу')
    ]

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    activity_type = models.CharField("Тип активности", max_length=20, choices=ACTIVITY_TYPES)
    created_by = models.ForeignKey(CustomUser, verbose_name="Создатель", related_name='activities', on_delete=models.CASCADE)
    photo_url = models.ImageField("Фото (опционально)", upload_to='activities/%Y/%m/%d', blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Активность приюта"
        verbose_name_plural = "Активности приюта"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
