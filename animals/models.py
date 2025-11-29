from django.db import models
from django.utils.text import slugify
from users.models import CustomUser

class Animal(models.Model):
    STATUS_CHOICES = [
        ('in_shelter', 'В приюте'),
        ('adopted', 'Усыновлено')
    ]

    name = models.CharField("Имя", max_length=100)
    species = models.CharField("Вид", max_length=50)
    breed = models.CharField("Порода", max_length=100, blank=True, null=True)
    age_years = models.PositiveIntegerField("Возраст (годы)", default=0)
    age_months = models.PositiveIntegerField("Возраст (месяцы)", default=0)
    health_status = models.TextField("Состояние здоровья")
    description = models.TextField("Описание/характер", blank=True, null=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='in_shelter')
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)
    slug = models.SlugField("Ссылка (slug)", max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Животное"
        verbose_name_plural = "Животные"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.species})"

    def save(self, *args, **kwargs):
        # Автоматически создаём slug из имени, если не указан
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Animal.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)



class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, related_name='photos', on_delete=models.CASCADE)
    photo_url = models.ImageField(upload_to='animals/%Y/%m/%d')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото {self.animal.name} ({self.id})"