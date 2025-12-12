from rest_framework import serializers
from .models import Animal, AnimalPhoto


class AnimalPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalPhoto
        fields = ['id', 'photo_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AnimalSerializer(serializers.ModelSerializer):
    photos = AnimalPhotoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Animal
        fields = ['id', 'name', 'species', 'breed', 'age_years', 'age_months', 
                  'health_status', 'description', 'status', 'status_display', 
                  'slug', 'created_at', 'photos']
        read_only_fields = ['id', 'slug', 'created_at']


class AnimalCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['name', 'species', 'breed', 'age_years', 'age_months', 
                  'health_status', 'description', 'status']
    
    def validate_age_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Возраст не может быть отрицательным")
        return value
    
    def validate_age_months(self, value):
        if value < 0:
            raise serializers.ValidationError("Возраст не может быть отрицательным")
        return value
    
    def validate_status(self, value):
        if value not in ['in_shelter', 'adopted']:
            raise serializers.ValidationError("Статус должен быть 'in_shelter' или 'adopted'")
        return value

