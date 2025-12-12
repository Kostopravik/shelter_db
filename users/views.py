from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .forms import RegisterForm, LoginForm
from .models import CustomUser
from .serializers import UserSerializer, UserCreateSerializer


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "adopter"  # фиксируем роль при регистрации
            user.save()
            login(request, user)
            return redirect("/")  # редирект на главную или ленту активностей
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/")


# API Views
class UserListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Администраторы видят всех пользователей, остальные - только себя
        if request.user.role == 'admin':
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(id=request.user.id)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Только администраторы могут создавать пользователей через API
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут создавать пользователей"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None
    
    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Пользователи могут видеть только себя, администраторы - всех
        if request.user.role != 'admin' and request.user.id != user.id:
            return Response(
                {"error": "Нет доступа к этому пользователю"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Пользователи могут редактировать только себя, администраторы - всех
        if request.user.role != 'admin' and request.user.id != user.id:
            return Response(
                {"error": "Нет доступа для редактирования этого пользователя"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        # Только администраторы могут удалять пользователей
        if request.user.role != 'admin':
            return Response(
                {"error": "Только администраторы могут удалять пользователей"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object(pk)
        if not user:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
