from django.contrib import admin
from .models import Adoption, Return

@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'animal', 'status', 'submitted_at', 'rejection_reason']
    list_filter = ['status', 'submitted_at']
    search_fields = ['user__username', 'animal__name']

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['adoption', 'reason', 'returned_at', 'processed_by']
    list_filter = ['returned_at', 'processed_by']
    search_fields = ['adoption__animal__name', 'adoption__user__username']
