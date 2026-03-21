from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('request-to-admin/', views.request_to_admin, name='request-to-admin'),
    path('send-otp/<str:otp_type>/', views.send_otp, name='send-otp'),
    path('verify-otp/<str:otp_type>/', views.verify_otp, name='verify-otp'),
    path('verification-required/', views.verification_required, name='verification-required'),
]