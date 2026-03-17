from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from pets.views import landing_page, lost_pets, found_pets, adoption_pets, golden_hour_list, admin_dashboard, admin_users, admin_abuse_reports, submit_general_abuse_report, admin_request_list, update_request_status, delete_request, admin_delete_user, admin_contact_requests, update_contact_request_status, admin_admin_requests, update_admin_request_status, submit_complaint, admin_system_complaints
from pet_portal.views import custom_404
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('admin/', admin.site.urls), 
    path('', landing_page, name='landing'),
    path('pets/', include('pets.urls')),
    path('accounts/', include('accounts.urls')),
    path('lost-pets/', lost_pets, name='lost-pets'),
    path('found-pets/', found_pets, name='found-pets'),
    path('adoption-pets/', adoption_pets, name='adoption-pets'),
    path('golden-hour/', golden_hour_list, name='golden-hour'),
    path('404/', custom_404, name='test_404'),
    
    # Info pages
    path('about/', TemplateView.as_view(template_name='info/about.html'), name='about'),
    path('careers/', TemplateView.as_view(template_name='info/careers.html'), name='careers'),
    path('volunteer/', TemplateView.as_view(template_name='info/volunteer.html'), name='volunteer'),
    path('pet-care-guides/', TemplateView.as_view(template_name='info/pet_care_guides.html'), name='pet-care-guides'),
    path('lost-pet-checklist/', TemplateView.as_view(template_name='info/lost_pet_checklist.html'), name='lost-pet-checklist'),
    path('found-pet-protocol/', TemplateView.as_view(template_name='info/found_pet_protocol.html'), name='found-pet-protocol'),
    path('report-abuse/', submit_general_abuse_report, name='submit-abuse-report'),
    path('submit-complaint/', submit_complaint, name='submit_complaint'),
    
    # Custom Admin/Staff Portal Routes
    path('staff/', admin_dashboard, name='custom-admin-dashboard'),
    path('staff/settings/', auth_views.PasswordChangeView.as_view(template_name='admin_portal/settings.html', success_url='/staff/'), name='staff-settings'),
    path('staff/users/', admin_users, name='custom-admin-users'),
    path('staff/users/<int:user_id>/delete/', admin_delete_user, name='admin-delete-user'),
    path('staff/abuse-reports/', admin_abuse_reports, name='custom-admin-abuse-reports'),
    path('staff/pet-reports/', admin_request_list, name='admin-request-list'),
    path('staff/pet-reports/<int:request_id>/status/', update_request_status, name='update-request-status'),
    path('staff/pet-reports/<int:request_id>/delete/', delete_request, name='delete-request'),
    path('staff/contact-requests/', admin_contact_requests, name='admin-contact-requests'),
    path('staff/contact-requests/<int:request_id>/status/', update_contact_request_status, name='update-contact-request-status'),
    path('staff/admin-requests/', admin_admin_requests, name='admin-admin-requests'),
    path('staff/admin-requests/<int:request_id>/status/', update_admin_request_status, name='update-admin-request-status'),
    path('staff/system-complaints/', admin_system_complaints, name='admin-system-complaints'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pet_portal.views.custom_404'
