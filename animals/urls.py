from django.urls import path
from .views import (
    AnimalListAPI, AnimalDetailAPI,
    AnimalPhotoListAPI, AnimalPhotoDetailAPI,
    animal_list, animal_detail, create_animal, edit_animal, delete_animal
)

urlpatterns = [
    # API endpoints
    path("api/animals/", AnimalListAPI.as_view(), name="api_animals"),
    path("api/animals/<int:pk>/", AnimalDetailAPI.as_view(), name="api_animal_detail"),
    path("api/animals/<int:animal_id>/photos/", AnimalPhotoListAPI.as_view(), name="api_animal_photos"),
    path("api/photos/<int:pk>/", AnimalPhotoDetailAPI.as_view(), name="api_photo_detail"),
    # Template views
    path("animals/", animal_list, name="animal_list"),
    path("animals/create/", create_animal, name="create_animal"),
    path("animals/<slug:slug>/", animal_detail, name="animal_detail"),
    path("animals/<slug:slug>/edit/", edit_animal, name="edit_animal"),
    path("animals/<slug:slug>/delete/", delete_animal, name="delete_animal"),
]

