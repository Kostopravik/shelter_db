from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Animal, AnimalPhoto
from .serializers import AnimalSerializer, AnimalCreateUpdateSerializer, AnimalPhotoSerializer
from adoptions.models import Adoption


class AnimalListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Фильтрация по виду животного
        species = request.query_params.get('species', None)
        status_filter = request.query_params.get('status', None)
        
        animals = Animal.objects.all()
        
        if species:
            animals = animals.filter(species__icontains=species)
        if status_filter:
            animals = animals.filter(status=status_filter)
        
        serializer = AnimalSerializer(animals, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Только администраторы и волонтёры могут создавать животных
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут добавлять животных"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AnimalCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            animal = serializer.save()
            response_serializer = AnimalSerializer(animal)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnimalDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Animal.objects.get(pk=pk)
        except Animal.DoesNotExist:
            return None
    
    def get(self, request, pk):
        animal = self.get_object(pk)
        if not animal:
            return Response(
                {"error": "Животное не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AnimalSerializer(animal)
        return Response(serializer.data)
    
    def put(self, request, pk):
        # Только администраторы и волонтёры могут редактировать животных
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут редактировать животных"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        animal = self.get_object(pk)
        if not animal:
            return Response(
                {"error": "Животное не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AnimalCreateUpdateSerializer(animal, data=request.data, partial=True)
        if serializer.is_valid():
            animal = serializer.save()
            response_serializer = AnimalSerializer(animal)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        # Только администраторы и волонтёры могут удалять животных
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут удалять животных"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        animal = self.get_object(pk)
        if not animal:
            return Response(
                {"error": "Животное не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        animal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnimalPhotoListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, animal_id):
        photos = AnimalPhoto.objects.filter(animal_id=animal_id)
        serializer = AnimalPhotoSerializer(photos, many=True)
        return Response(serializer.data)
    
    def post(self, request, animal_id):
        # Только администраторы и волонтёры могут загружать фотографии
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут загружать фотографии"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            animal = Animal.objects.get(pk=animal_id)
        except Animal.DoesNotExist:
            return Response(
                {"error": "Животное не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверка формата файла
        if 'photo_url' in request.FILES:
            file = request.FILES['photo_url']
            if not file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                return Response(
                    {"error": "Разрешены только форматы .jpg и .png"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = AnimalPhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(animal=animal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnimalPhotoDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return AnimalPhoto.objects.get(pk=pk)
        except AnimalPhoto.DoesNotExist:
            return None
    
    def get(self, request, pk):
        photo = self.get_object(pk)
        if not photo:
            return Response(
                {"error": "Фотография не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AnimalPhotoSerializer(photo)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        # Только администраторы и волонтёры могут удалять фотографии
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут удалять фотографии"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        photo = self.get_object(pk)
        if not photo:
            return Response(
                {"error": "Фотография не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Views для шаблонов
def animal_list(request):
    """Список всех животных с карточками"""
    animals = Animal.objects.exclude(slug='').order_by('-created_at')
    
    # Фильтрация по виду
    species = request.GET.get('species', '')
    if species:
        animals = animals.filter(species__icontains=species)
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        animals = animals.filter(status=status_filter)
    
    # Добавляем фотографии для каждого животного
    for animal in animals:
        photos = AnimalPhoto.objects.filter(animal=animal)
        animal.photos_list = list(photos)
        animal.first_photo = photos.first() if photos.exists() else None
    
    return render(request, 'animals/list.html', {
        'animals': animals,
        'selected_species': species,
        'selected_status': status_filter,
        'status_choices': Animal.STATUS_CHOICES
    })


def animal_detail(request, slug):
    """Детальная страница животного с формой заявки"""
    animal = get_object_or_404(Animal, slug=slug)
    photos = AnimalPhoto.objects.filter(animal=animal)
    
    # Проверяем, есть ли уже заявка от текущего пользователя
    has_adoption = False
    existing_adoption = None
    if request.user.is_authenticated:
        existing_adoption = Adoption.objects.filter(
            user=request.user,
            animal=animal
        ).first()
        if existing_adoption:
            has_adoption = True
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Запрещаем подачу заявок волонтёрам и админам
        if request.user.role in ['admin', 'volunteer']:
            messages.error(request, 'Волонтёры и администраторы не могут подавать заявки на усыновление')
            return redirect('animal_detail', slug=slug)
        
        # Создание заявки
        if has_adoption:
            messages.error(request, 'У вас уже есть заявка на это животное')
        elif animal.status != 'in_shelter':
            messages.error(request, 'Это животное уже усыновлено')
        else:
            # Обновляем анкету пользователя, если он усыновитель
            if request.user.role == 'adopter':
                has_experience = request.POST.get('has_experience') == 'on'
                has_other_pets = request.POST.get('has_other_pets') == 'on'
                ready_for_pet = request.POST.get('ready_for_pet', '')
                
                request.user.has_experience = has_experience
                request.user.has_other_pets = has_other_pets
                request.user.ready_for_pet = ready_for_pet
                request.user.save()
            
            adoption = Adoption.objects.create(
                user=request.user,
                animal=animal,
                status='pending',
                rejection_reason=''
            )
            messages.success(request, 'Заявка успешно подана!')
            return redirect('animal_detail', slug=slug)
    
    return render(request, 'animals/detail.html', {
        'animal': animal,
        'photos': photos,
        'has_adoption': has_adoption,
        'existing_adoption': existing_adoption
    })


@login_required
def create_animal(request):
    """Создание нового животного"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут добавлять животных')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        species = request.POST.get('species')
        breed = request.POST.get('breed', '')
        age_years = int(request.POST.get('age_years', 0) or 0)
        age_months = int(request.POST.get('age_months', 0) or 0)
        health_status = request.POST.get('health_status')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'in_shelter')
        photos = request.FILES.getlist('photos')
        
        if not name or not species or not health_status:
            messages.error(request, 'Заполните все обязательные поля')
        else:
            animal = Animal(
                name=name,
                species=species,
                breed=breed if breed else None,
                age_years=age_years,
                age_months=age_months,
                health_status=health_status,
                description=description if description else None,
                status=status
            )
            # Сохраняем, чтобы slug был создан автоматически
            animal.save()
            
            # Обновляем объект из БД, чтобы получить созданный slug
            animal.refresh_from_db()
            
            # Загружаем фотографии
            for photo in photos:
                AnimalPhoto.objects.create(animal=animal, photo_url=photo)
            
            messages.success(request, f'Животное {animal.name} успешно добавлено!')
            # Проверяем, что slug создан
            if animal.slug:
                return redirect('animal_detail', slug=animal.slug)
            else:
                # Если slug не создан, перенаправляем на список
                messages.warning(request, 'Животное добавлено, но возникла проблема с созданием ссылки')
                return redirect('animal_list')
    
    return render(request, 'animals/create.html', {
        'status_choices': Animal.STATUS_CHOICES
    })


@login_required
def edit_animal(request, slug):
    """Редактирование животного"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут редактировать животных')
        return redirect('home')
    
    animal = get_object_or_404(Animal, slug=slug)
    
    if request.method == 'POST':
        animal.name = request.POST.get('name')
        animal.species = request.POST.get('species')
        animal.breed = request.POST.get('breed', '')
        animal.age_years = int(request.POST.get('age_years', 0) or 0)
        animal.age_months = int(request.POST.get('age_months', 0) or 0)
        animal.health_status = request.POST.get('health_status')
        animal.description = request.POST.get('description', '')
        animal.status = request.POST.get('status', 'in_shelter')
        new_photos = request.FILES.getlist('photos')
        delete_photo_ids = request.POST.getlist('delete_photos')
        
        if not animal.name or not animal.species or not animal.health_status:
            messages.error(request, 'Заполните все обязательные поля')
        else:
            animal.breed = animal.breed if animal.breed else None
            animal.description = animal.description if animal.description else None
            animal.save()
            
            # Удаляем отмеченные фотографии
            if delete_photo_ids:
                AnimalPhoto.objects.filter(id__in=delete_photo_ids, animal=animal).delete()
            
            # Загружаем новые фотографии (можно добавить сразу несколько)
            for photo in new_photos:
                AnimalPhoto.objects.create(animal=animal, photo_url=photo)
            
            messages.success(request, f'Животное {animal.name} успешно обновлено!')
            return redirect('animal_detail', slug=animal.slug)
    
    photos = AnimalPhoto.objects.filter(animal=animal)
    return render(request, 'animals/edit.html', {
        'animal': animal,
        'photos': photos,
        'status_choices': Animal.STATUS_CHOICES
    })


@login_required
def delete_animal(request, slug):
    """Удаление животного"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут удалять животных')
        return redirect('home')
    
    animal = get_object_or_404(Animal, slug=slug)
    
    if request.method == 'POST':
        animal_name = animal.name
        animal.delete()
        messages.success(request, f'Животное {animal_name} успешно удалено')
        return redirect('animal_list')
    
    return render(request, 'animals/delete_confirm.html', {'animal': animal})
