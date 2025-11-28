from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'has_experience', 'has_other_pets', 'ready_for_pet')}),
    )
