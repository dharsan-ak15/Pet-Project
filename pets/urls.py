from . import views
from django.urls import path

from .views import (
    create_pet_request,
    search_pets,
    admin_request_list,
    update_request_status,
    delete_request,
    profile_view,
)

urlpatterns = [
    path('report/', views.create_pet_request, name='report-pet'),
    path('report/<int:request_id>/edit/', views.edit_pet_request, name='edit-pet-request'),
    path('report/<int:request_id>/delete/', views.delete_pet_request, name='delete-pet-request'),
    path('search/', search_pets, name='search-pets'),
    
    path('admin/requests/', admin_request_list, name='admin-request-list'),
    path('admin/requests/<int:request_id>/status/', update_request_status, name='update-request-status'),
    path('admin/requests/<int:request_id>/delete/', delete_request, name='delete-request'),
    path('pet/<int:request_id>/', views.pet_detail, name='pet-detail'),
    path('report/<int:request_id>/reunited/', views.mark_reunited, name='mark-reunited'),
]

