from django.contrib import admin
from .models import Animal, AnimalPhoto

class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1  # сколько пустых форм будет изначально
    readonly_fields = ['uploaded_at']  # дату загруки не меняем


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'breed', 'age_years', 'age_months', 'status', 'created_at', 'slug']
    list_filter = ['species', 'status', 'created_at']
    search_fields = ['name', 'species', 'breed']
    ordering = ['name']
    # Поля, которые отображаются при добавлении/редактировании животного
    fields = ['name', 'species', 'breed', 'age_years', 'age_months', 'health_status', 'description', 'status', 'slug', 'created_at']
    readonly_fields = ['slug', 'created_at']

    inlines = [AnimalPhotoInline]