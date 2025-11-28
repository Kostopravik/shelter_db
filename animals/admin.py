from django.contrib import admin
from .models import Animal, AnimalPhoto


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'breed', 'age_years', 'age_months', 'status', 'created_at']
    list_filter = ['species', 'status', 'created_at']
    search_fields = ['name', 'species', 'breed']
    ordering = ['name']


@admin.register(AnimalPhoto)
class AnimalPhotoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'photo_url', 'uploaded_at']
    list_filter = ['animal', 'uploaded_at']
