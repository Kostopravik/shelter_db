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

    title = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_by = models.ForeignKey(CustomUser, related_name='activities', on_delete=models.CASCADE)
    photo_url = models.ImageField(upload_to='activities/%Y/%m/%d', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
