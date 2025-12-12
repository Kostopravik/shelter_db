from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    list_editable = ['role']  # Можно редактировать роль прямо в списке

    fieldsets = UserAdmin.fieldsets + (
        ("Роль и дополнительные поля", {
            'fields': ('role', 'has_experience', 'has_other_pets', 'ready_for_pet', 'slug', 'created_at')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Роль и дополнительные поля", {
            'fields': ('role', 'has_experience', 'has_other_pets', 'ready_for_pet')
        }),
    )
    
    readonly_fields = ['slug', 'created_at']  # slug и дата регистрации не редактируются вручную
