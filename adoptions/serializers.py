from rest_framework import serializers
from .models import Adoption, Return
from users.models import CustomUser
from animals.models import Animal


class AdoptionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Adoption
        fields = ['id', 'user', 'user_username', 'animal', 'animal_name', 
                  'status', 'status_display', 'submitted_at', 'rejection_reason']
        read_only_fields = ['id', 'submitted_at']
    
    def validate(self, data):
        # Если статус меняется на rejected, проверяем наличие rejection_reason
        if 'status' in data and data['status'] == 'rejected':
            if 'rejection_reason' not in data or not data.get('rejection_reason'):
                # Если это обновление существующей записи, проверяем текущее значение
                if self.instance and not self.instance.rejection_reason:
                    raise serializers.ValidationError({
                        'rejection_reason': "При отклонении заявки необходимо указать причину отклонения"
                    })
                elif not self.instance:
                    raise serializers.ValidationError({
                        'rejection_reason': "При отклонении заявки необходимо указать причину отклонения"
                    })
        return data


class AdoptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adoption
        fields = ['animal']
    
    def validate(self, data):
        user = self.context['request'].user
        animal = data['animal']
        
        # Проверка: один пользователь не может подать более одной активной заявки на одного питомца
        existing_adoption = Adoption.objects.filter(
            user=user, 
            animal=animal,
            status__in=['pending', 'approved']
        ).first()
        
        if existing_adoption:
            raise serializers.ValidationError(
                "У вас уже есть активная заявка на это животное"
            )
        
        # Проверка: можно подавать заявку только на животное со статусом in_shelter
        if animal.status != 'in_shelter':
            raise serializers.ValidationError(
                "Заявку можно подать только на животное со статусом 'in_shelter'"
            )
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'pending'
        validated_data['rejection_reason'] = ''  # Пустое значение по умолчанию для pending
        return super().create(validated_data)


class ReturnSerializer(serializers.ModelSerializer):
    adoption_id = serializers.IntegerField(source='adoption.id', read_only=True)
    animal_name = serializers.CharField(source='adoption.animal.name', read_only=True)
    user_username = serializers.CharField(source='adoption.user.username', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Return
        fields = ['id', 'adoption', 'adoption_id', 'animal_name', 'user_username', 
                  'reason', 'returned_at', 'processed_by', 'processed_by_username']
        read_only_fields = ['id', 'returned_at']


class ReturnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = ['adoption', 'reason']
    
    def validate(self, data):
        adoption = data['adoption']
        
        # Проверка: возврат можно оформить только для одобренной заявки
        if adoption.status != 'approved':
            raise serializers.ValidationError(
                "Возврат можно оформить только для одобренной заявки"
            )
        
        # Проверка: проверяем, что возврат еще не был оформлен
        if hasattr(adoption, 'return_record'):
            raise serializers.ValidationError(
                "Возврат для этой заявки уже был оформлен"
            )
        
        return data
    
    def create(self, validated_data):
        validated_data['processed_by'] = self.context['request'].user
        return_obj = super().create(validated_data)
        
        # Обновляем статус заявки и животного
        adoption = validated_data['adoption']
        adoption.status = 'returned'
        adoption.save()
        
        animal = adoption.animal
        animal.status = 'in_shelter'
        animal.save()
        
        return return_obj

