from . import views
from django.urls import path

from .views import (
    create_pet_request,
    search_pets,
    profile_view,
)

urlpatterns = [
    path('report/', views.create_pet_request, name='report-pet'),
    path('report/<int:request_id>/edit/', views.edit_pet_request, name='edit-pet-request'),
    path('report/<int:request_id>/delete/', views.delete_pet_request, name='delete-pet-request'),
    path('search/', search_pets, name='search-pets'),
    
    path('pet/<int:request_id>/', views.pet_detail, name='pet-detail'),
    path('report/<int:request_id>/reunited/', views.mark_reunited, name='mark-reunited'),
]

