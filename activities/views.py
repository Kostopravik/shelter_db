# activities/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Activity
from .serializers import ActivitySerializer


def home(request):
    """Главная страница с лентой активностей и карточками животных"""
    from animals.models import Animal, AnimalPhoto
    
    activities = Activity.objects.order_by('-created_at')[:10]  # Последние 10 активностей
    animals = Animal.objects.exclude(slug='').order_by('-created_at')[:6]  # Последние 6 животных с slug (все статусы)
    
    # Добавляем фотографии для каждого животного
    for animal in animals:
        photos = AnimalPhoto.objects.filter(animal=animal)
        animal.photos_list = list(photos)
        animal.first_photo = photos.first() if photos.exists() else None
    
    return render(request, 'activities/home.html', {
        'activities': activities,
        'animals': animals
    })


def activity_feed(request):
    """Представление для отображения ленты активностей (шаблон)"""
    activities = Activity.objects.order_by('-created_at')
    return render(request, 'activities/feed.html', {'activities': activities})


@login_required
def delete_activity(request, pk):
    """Удаление активности"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут удалять активности')
        return redirect('home')
    
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Активность успешно удалена')
        return redirect('home')
    
    return render(request, 'activities/delete_confirm.html', {'activity': activity})


@login_required
def create_activity(request):
    """Создание новой активности"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут создавать активности')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        activity_type = request.POST.get('activity_type')
        photo = request.FILES.get('photo_url')
        
        if not title or not description or not activity_type:
            messages.error(request, 'Заполните все обязательные поля')
        else:
            activity = Activity.objects.create(
                title=title,
                description=description,
                activity_type=activity_type,
                created_by=request.user,
                photo_url=photo if photo else None
            )
            messages.success(request, 'Активность успешно создана!')
            return redirect('home')
    
    return render(request, 'activities/create.html', {
        'activity_types': Activity.ACTIVITY_TYPES
    })


@login_required
def edit_activity(request, pk):
    """Редактирование активности"""
    if request.user.role not in ['admin', 'volunteer']:
        messages.error(request, 'Только администраторы и волонтёры могут редактировать активности')
        return redirect('home')
    
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        activity.title = request.POST.get('title')
        activity.description = request.POST.get('description')
        activity.activity_type = request.POST.get('activity_type')
        
        if 'photo_url' in request.FILES:
            activity.photo_url = request.FILES['photo_url']
        elif 'clear_photo' in request.POST:
            activity.photo_url = None
        
        if not activity.title or not activity.description or not activity.activity_type:
            messages.error(request, 'Заполните все обязательные поля')
        else:
            activity.save()
            messages.success(request, 'Активность успешно обновлена!')
            return redirect('home')
    
    return render(request, 'activities/edit.html', {
        'activity': activity,
        'activity_types': Activity.ACTIVITY_TYPES
    })

class ActivityListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Все пользователи могут просматривать активности
        activities = Activity.objects.order_by('-created_at')
        
        # Фильтрация по типу активности
        activity_type = request.query_params.get('activity_type', None)
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Только администраторы и волонтёры могут создавать активности
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут создавать активности"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            # Автоматически устанавливаем создателя
            activity = serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivityDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return None
    
    def get(self, request, pk):
        activity = self.get_object(pk)
        if not activity:
            return Response(
                {"error": "Активность не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ActivitySerializer(activity)
        return Response(serializer.data)
    
    def put(self, request, pk):
        # Только администраторы и волонтёры могут редактировать активности
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут редактировать активности"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activity = self.get_object(pk)
        if not activity:
            return Response(
                {"error": "Активность не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ActivitySerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        # Только администраторы и волонтёры могут удалять активности
        if request.user.role not in ['admin', 'volunteer']:
            return Response(
                {"error": "Только администраторы и волонтёры могут удалять активности"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activity = self.get_object(pk)
        if not activity:
            return Response(
                {"error": "Активность не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
