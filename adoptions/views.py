from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Adoption, Return
from .serializers import (
    AdoptionSerializer, AdoptionCreateSerializer,
    ReturnSerializer, ReturnCreateSerializer
)


# Views для шаблонов
@login_required
def adoption_list(request):
    """Список заявок для администраторов, волонтёров и пользователей (свои заявки)"""
    # Администраторы и волонтёры видят все заявки, остальные - только свои
    if request.user.role in ['admin', 'volunteer']:
        adoptions = Adoption.objects.all().order_by('-submitted_at')
    else:
        adoptions = Adoption.objects.filter(user=request.user).order_by('-submitted_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        adoptions = adoptions.filter(status=status_filter)
    
    # Быстрое изменение статуса для админов
    if request.method == 'POST' and request.user.role == 'admin':
        adoption_id = request.POST.get('adoption_id')
        new_status = request.POST.get('new_status')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        try:
            adoption = Adoption.objects.get(pk=adoption_id)
            old_status = adoption.status
            
            if new_status == 'rejected' and not rejection_reason:
                messages.error(request, 'При отклонении заявки необходимо указать причину')
            else:
                adoption.status = new_status
                if new_status == 'rejected':
                    adoption.rejection_reason = rejection_reason
                adoption.save()
                
                # Если заявка одобрена, обновляем статус животного
                if new_status == 'approved' and old_status != 'approved':
                    adoption.animal.status = 'adopted'
                    adoption.animal.save()
                    # Отклоняем остальные активные заявки
                    Adoption.objects.filter(
                        animal=adoption.animal,
                        status='pending'
                    ).exclude(id=adoption.id).update(
                        status='rejected',
                        rejection_reason='Заявка отклонена: животное было усыновлено другим пользователем'
                    )
                
                messages.success(request, 'Статус заявки успешно изменён')
        except Adoption.DoesNotExist:
            messages.error(request, 'Заявка не найдена')
        
        return redirect('adoption_list')
    
    return render(request, 'adoptions/list.html', {
        'adoptions': adoptions,
        'selected_status': status_filter,
        'is_admin': request.user.role == 'admin',
        'is_admin_or_volunteer': request.user.role in ['admin', 'volunteer']
    })


@login_required
def adoption_detail(request, pk):
    """Детальная страница заявки"""
    adoption = get_object_or_404(Adoption, pk=pk)
    
    # Проверка доступа
    if request.user.role not in ['admin', 'volunteer'] and adoption.user != request.user:
        messages.error(request, 'У вас нет доступа к этой заявке')
        return redirect('home')
    
    if request.method == 'POST' and request.user.role == 'admin':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Одобрение заявки
            old_status = adoption.status
            adoption.status = 'approved'
            adoption.save()
            
            # Обновляем статус животного
            adoption.animal.status = 'adopted'
            adoption.animal.save()
            
            # Отклоняем остальные активные заявки
            Adoption.objects.filter(
                animal=adoption.animal,
                status='pending'
            ).exclude(id=adoption.id).update(
                status='rejected',
                rejection_reason='Заявка отклонена: животное было усыновлено другим пользователем'
            )
            
            messages.success(request, f'Заявка одобрена. Животное {adoption.animal.name} теперь усыновлено.')
            
        elif action == 'reject':
            # Отклонение заявки
            rejection_reason = request.POST.get('rejection_reason', '')
            if not rejection_reason:
                messages.error(request, 'Необходимо указать причину отклонения')
            else:
                adoption.status = 'rejected'
                adoption.rejection_reason = rejection_reason
                adoption.save()
                messages.success(request, 'Заявка отклонена')
        
        elif action == 'return':
            # Оформление возврата
            reason = request.POST.get('reason', '')
            if adoption.user != request.user:
                messages.error(request, 'Вы можете оформить возврат только для своих заявок')
            elif not reason:
                messages.error(request, 'Необходимо указать причину возврата')
            elif adoption.status != 'approved':
                messages.error(request, 'Возврат можно оформить только для одобренной заявки')
            elif hasattr(adoption, 'return_record'):
                messages.error(request, 'Возврат для этой заявки уже был оформлен')
            else:
                Return.objects.create(
                    adoption=adoption,
                    reason=reason,
                    processed_by=request.user
                )
                adoption.status = 'returned'
                adoption.save()
                adoption.animal.status = 'in_shelter'
                adoption.animal.save()
                messages.success(
                    request,
                    'Возврат успешно оформлен. Для всех деталей свяжитесь с нами по номеру +7 000 0000 0000'
                )
        
        return redirect('adoption_detail', pk=pk)
    
    # Проверяем наличие возврата
    has_return = hasattr(adoption, 'return_record')
    
    return render(request, 'adoptions/detail.html', {
        'adoption': adoption,
        'is_admin': request.user.role == 'admin',
        'user': request.user,
        'has_return': has_return
    })


@login_required
def return_list(request):
    """Список возвратов для всех пользователей"""
    # Администраторы и волонтёры видят все возвраты, остальные - только свои
    if request.user.role in ['admin', 'volunteer']:
        returns = Return.objects.all().order_by('-returned_at')
    else:
        returns = Return.objects.filter(adoption__user=request.user).order_by('-returned_at')

    # Для оформления возврата всегда показываем только одобренные заявки текущего пользователя,
    # чтобы никто не мог оформить возврат по чужой заявке
    approved_adoptions = Adoption.objects.filter(
        user=request.user,
        status='approved'
    ).exclude(return_record__isnull=False).order_by('-submitted_at')
    
    # Обработка оформления возврата
    if request.method == 'POST':
        adoption_id = request.POST.get('adoption_id')
        reason = request.POST.get('reason', '')
        
        if not reason:
            messages.error(request, 'Необходимо указать причину возврата')
        else:
            try:
                adoption = Adoption.objects.get(pk=adoption_id)
                # Проверка доступа: возврат можно оформить только по своей заявке,
                # даже если пользователь администратор или волонтёр
                if adoption.user != request.user:
                    messages.error(request, 'Вы можете оформить возврат только для своих заявок')
                elif adoption.status != 'approved':
                    messages.error(request, 'Возврат можно оформить только для одобренной заявки')
                elif hasattr(adoption, 'return_record'):
                    messages.error(request, 'Возврат для этой заявки уже был оформлен')
                else:
                    Return.objects.create(
                        adoption=adoption,
                        reason=reason,
                        # processed_by заполняется сотрудником приюта при необходимости
                        processed_by=None
                    )
                    adoption.status = 'returned'
                    adoption.save()
                    adoption.animal.status = 'in_shelter'
                    adoption.animal.save()
                    messages.success(
                        request,
                        'Возврат успешно оформлен. Для всех деталей свяжитесь с нами по номеру +7 000 0000 0000'
                    )
            except Adoption.DoesNotExist:
                messages.error(request, 'Заявка не найдена')
        
        return redirect('return_list')
    
    return render(request, 'adoptions/returns.html', {
        'returns': returns,
        'approved_adoptions': approved_adoptions,
        'is_admin_or_volunteer': request.user.role in ['admin', 'volunteer'],
        'can_create_return': True  # Все пользователи могут оформить возврат для своих одобренных заявок
    })


# API Views
class AdoptionListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Администраторы и волонтёры видят все заявки, остальные - только свои
        if request.user.role in ['admin', 'volunteer']:
            adoptions = Adoption.objects.all()
        else:
            adoptions = Adoption.objects.filter(user=request.user)
        
        # Фильтрация по статусу
        status_filter = request.query_params.get('status', None)
        if status_filter:
            adoptions = adoptions.filter(status=status_filter)
        
        serializer = AdoptionSerializer(adoptions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Все авторизованные пользователи могут подавать заявки
        serializer = AdoptionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            adoption = serializer.save()
            response_serializer = AdoptionSerializer(adoption)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdoptionDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Adoption.objects.get(pk=pk)
        except Adoption.DoesNotExist:
            return None
    
    def get(self, request, pk):
        adoption = self.get_object(pk)
        if not adoption:
            return Response(
                {"error": "Заявка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Пользователи могут видеть только свои заявки, администраторы и волонтёры - все
        if request.user.role not in ['admin', 'volunteer'] and adoption.user != request.user:
            return Response(
                {"error": "Нет доступа к этой заявке"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AdoptionSerializer(adoption)
        return Response(serializer.data)
    
    def put(self, request, pk):
        # Только администраторы могут изменять статус заявок
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут изменять статус заявок"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        adoption = self.get_object(pk)
        if not adoption:
            return Response(
                {"error": "Заявка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        old_status = adoption.status
        
        # Если статус меняется на rejected, проверяем наличие rejection_reason
        if 'status' in request.data and request.data['status'] == 'rejected':
            if 'rejection_reason' not in request.data or not request.data['rejection_reason']:
                return Response(
                    {"error": "При отклонении заявки необходимо указать причину отклонения"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = AdoptionSerializer(adoption, data=request.data, partial=True)
        if serializer.is_valid():
            adoption = serializer.save()
            
            # Если заявка одобрена, обновляем статус животного и отклоняем другие заявки
            if adoption.status == 'approved' and old_status != 'approved':
                # Обновляем статус животного
                adoption.animal.status = 'adopted'
                adoption.animal.save()
                
                # Отклоняем все остальные активные заявки на это животное
                Adoption.objects.filter(
                    animal=adoption.animal,
                    status='pending'
                ).exclude(id=adoption.id).update(status='rejected', rejection_reason='Заявка отклонена: животное было усыновлено другим пользователем')
            
            # Если заявка отклонена, животное остается доступным
            elif adoption.status == 'rejected' and old_status == 'approved':
                # Если была одобрена, но теперь отклонена, возвращаем животное в приют
                adoption.animal.status = 'in_shelter'
                adoption.animal.save()
            
            response_serializer = AdoptionSerializer(adoption)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        # Только администраторы могут удалять заявки
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут удалять заявки"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        adoption = self.get_object(pk)
        if not adoption:
            return Response(
                {"error": "Заявка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        adoption.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReturnListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Администраторы и волонтёры видят все возвраты, остальные - только свои
        if request.user.role in ['admin', 'volunteer']:
            returns = Return.objects.all()
        else:
            returns = Return.objects.filter(adoption__user=request.user)
        
        serializer = ReturnSerializer(returns, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Только администраторы могут оформлять возвраты
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут оформлять возвраты"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReturnCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return_obj = serializer.save()
            response_serializer = ReturnSerializer(return_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReturnDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Return.objects.get(pk=pk)
        except Return.DoesNotExist:
            return None
    
    def get(self, request, pk):
        return_obj = self.get_object(pk)
        if not return_obj:
            return Response(
                {"error": "Возврат не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Пользователи могут видеть только свои возвраты, администраторы и волонтёры - все
        if request.user.role not in ['admin', 'volunteer'] and return_obj.adoption.user != request.user:
            return Response(
                {"error": "Нет доступа к этому возврату"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReturnSerializer(return_obj)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        # Только администраторы могут удалять возвраты
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут удалять возвраты"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return_obj = self.get_object(pk)
        if not return_obj:
            return Response(
                {"error": "Возврат не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
