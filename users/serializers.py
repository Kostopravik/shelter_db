from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'has_experience', 'has_other_pets', 
                  'ready_for_pet', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'has_experience', 
                  'has_other_pets', 'ready_for_pet']
    
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

