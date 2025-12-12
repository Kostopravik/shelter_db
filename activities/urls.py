# activities/urls.py
from django.urls import path
from .views import home, activity_feed, create_activity, edit_activity, delete_activity, ActivityListAPI, ActivityDetailAPI

urlpatterns = [
    path("", home, name="home"),  # Главная страница
    path("feed/", activity_feed, name="activity_feed"),  # Полная лента активностей
    path("activities/create/", create_activity, name="create_activity"),  # Создание активности
    path("activities/<int:pk>/edit/", edit_activity, name="edit_activity"),  # Редактирование активности
    path("activities/<int:pk>/delete/", delete_activity, name="delete_activity"),  # Удаление активности
    path("api/activities/", ActivityListAPI.as_view(), name="api_activities"),  # для API
    path("api/activities/<int:pk>/", ActivityDetailAPI.as_view(), name="api_activity_detail"),  # для API
]
