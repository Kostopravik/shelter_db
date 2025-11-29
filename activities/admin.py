from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_type', 'created_by', 'created_at']
    list_filter = ['activity_type', 'created_by', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    fields = ['title', 'description', 'activity_type', 'created_by', 'photo_url', 'created_at']
    readonly_fields = ['created_at']
