from django.urls import path
from .views import login_view, logout_view, register_view, UserListAPI, UserDetailAPI

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/users/", UserListAPI.as_view(), name="api_users"),
    path("api/users/<int:pk>/", UserDetailAPI.as_view(), name="api_user_detail"),
]
