from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'created_at', 'slug']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_active', 'is_staff']

    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительные поля", {
            'fields': ('role', 'has_experience', 'has_other_pets', 'ready_for_pet', 'slug')
        }),
    )
    readonly_fields = ['slug', 'created_at']  # slug и дата регистрации не редактируются вручную
