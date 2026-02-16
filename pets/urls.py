from django.urls import path

from .views import admin_request_list, create_pet_request, delete_request, search_pets, update_request_status

urlpatterns = [
    path('report/', create_pet_request, name='report-pet'),
    path('search/', search_pets, name='search-pets'),
    path('admin/requests/', admin_request_list, name='admin-request-list'),
    path('admin/requests/<int:request_id>/status/', update_request_status, name='update-request-status'),
    path('admin/requests/<int:request_id>/delete/', delete_request, name='delete-request'),
]
