from django.shortcuts import redirect
from django.urls import reverse

class VerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check authenticated users who are not staff
        if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
            profile = getattr(request.user, 'profile', None)
            
            # If profile doesn't exist (shouldn't happen with signals) or not fully verified
            if not profile or not (profile.is_phone_verified and profile.is_email_verified):
                
                # Allowed paths while unverified
                allowed_url_names = [
                    'verification-required',
                    'send-otp',
                    'verify-otp',
                    'logout',
                    'profile',
                ]
                
                # Check if current path corresponds to an allowed URL name
                from django.urls import resolve
                try:
                    current_url_name = resolve(request.path_info).url_name
                except:
                    current_url_name = None

                # Specific check for paths that should ALWAYS be allowed (static, media, admin)
                if (current_url_name not in allowed_url_names and 
                    not request.path.startswith('/static/') and 
                    not request.path.startswith('/media/') and
                    not request.path.startswith('/admin/')):
                    return redirect('verification-required')
        
        return self.get_response(request)
