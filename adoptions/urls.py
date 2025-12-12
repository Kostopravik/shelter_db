from django.urls import path
from .views import (
    AdoptionListAPI, AdoptionDetailAPI,
    ReturnListAPI, ReturnDetailAPI,
    adoption_list, adoption_detail, return_list
)

urlpatterns = [
    # API endpoints
    path("api/adoptions/", AdoptionListAPI.as_view(), name="api_adoptions"),
    path("api/adoptions/<int:pk>/", AdoptionDetailAPI.as_view(), name="api_adoption_detail"),
    path("api/returns/", ReturnListAPI.as_view(), name="api_returns"),
    path("api/returns/<int:pk>/", ReturnDetailAPI.as_view(), name="api_return_detail"),
    # Template views
    path("adoptions/", adoption_list, name="adoption_list"),
    path("adoptions/<int:pk>/", adoption_detail, name="adoption_detail"),
    path("returns/", return_list, name="return_list"),
]

