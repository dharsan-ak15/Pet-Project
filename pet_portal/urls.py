
from django.contrib import admin
from django.urls import include, path
from pets.views import landing_page, lost_pets, found_pets
from accounts.views import register
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('admin/', admin.site.urls), 
    path('', landing_page, name='landing'),
    path('pets/', include('pets.urls')),
    path('accounts/', include('accounts.urls')),
    path('lost-pets/', lost_pets, name='lost-pets'),
    path('found-pets/', found_pets, name='found-pets'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

