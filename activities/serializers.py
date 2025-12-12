from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'activity_type', 'photo_url', 
                  'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
