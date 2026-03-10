from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from pets.views import landing_page, lost_pets, found_pets, adoption_pets, golden_hour_list, admin_dashboard, admin_users, staff_login_view, admin_abuse_reports, submit_general_abuse_report
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
    
    # Custom Admin Portal Routes
    path('portal/login/', staff_login_view, name='custom-admin-login'),
    path('portal/', admin_dashboard, name='custom-admin-dashboard'),
    path('portal/users/', admin_users, name='custom-admin-users'),
    path('portal/abuse-reports/', admin_abuse_reports, name='custom-admin-abuse-reports'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pet_portal.views.custom_404'
