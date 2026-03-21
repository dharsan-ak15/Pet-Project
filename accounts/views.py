from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, ProfileUpdateForm
from pets.models import Notification, PetRequest
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import random
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification, Profile
from .forms import CustomUserRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('custom-admin-dashboard')
        return redirect('landing')

    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            
            # Trigger both OTPs
            for otp_type in ['Email', 'Phone']:
                otp_code = str(random.randint(100000, 999999))
                OTPVerification.objects.create(user=user, otp_code=otp_code, otp_type=otp_type)
                # Simulated Sending
                target = user.email if otp_type == 'Email' else user.profile.phone
                print(f"[REGISTRATION OTP] To: {target} ({otp_type}) | Code: {otp_code}")

            messages.success(request, 'Account created! Please verify your email and phone number to continue.')
            return redirect('verification-required')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('custom-admin-dashboard')
        return redirect('landing')

    registration_success = request.session.pop('registration_success', False)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            if user.is_staff or user.is_superuser:
                return redirect('custom-admin-dashboard')
            return redirect('landing')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'registration_success': registration_success})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    from pets.models import PetContactRequest
    pet_requests = PetRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')

    contact_requests = PetContactRequest.objects.filter(
        requester=request.user
    ).select_related('pet').order_by('-created_at')

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')

    # ✅ SAFE for MySQL (no subquery update)
    popup_notifications = []
    for notification in unread_notifications:
        # Check if it's an approval or rejection
        msg = notification.message.lower()
        if 'accepted' in msg or 'declined' in msg or 'approved' in msg or 'rejected' in msg:
            popup_notifications.append({
                'id': notification.id,
                'message': notification.message,
                'type': 'success' if ('accepted' in msg or 'approved' in msg) else 'error',
                'reason': notification.pet_request.rejection_reason if (notification.pet_request and ('declined' in msg or 'rejected' in msg)) else None
            })
        notification.is_read = True
        notification.save()

    # Fetch all notifications after marking read
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(pet_requests, 10) # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Suggestion Engine Logic
    suggested_pets = None
    try:
        profile = request.user.profile
    except Exception:
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)

    # Only try to suggest if they have specified what they want or where they are
    if (profile.preferred_pet_type and profile.preferred_pet_type != 'None') or profile.city:
        query = Q(status='Accepted') & ~Q(user=request.user)
        if profile.preferred_pet_type and profile.preferred_pet_type != 'None':
            query &= Q(pet_type=profile.preferred_pet_type)
        if profile.city:
            district = profile.city.split(', ')[-1] if ', ' in profile.city else profile.city
            query &= Q(location__icontains=district)
        suggested_pets = PetRequest.objects.filter(query).order_by('-created_at')[:3]

    context = {
        'pet_requests': page_obj,
        'contact_requests': contact_requests,
        'notifications': notifications,
        'suggested_pets': suggested_pets,
        'popup_notifications': popup_notifications,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def request_to_admin(request):
    from .forms import AdminRequestForm
    from .models import AdminRequest
    
    # Check if they already have a pending request
    existing_request = AdminRequest.objects.filter(user=request.user, status='Pending').first()
    last_rejected_request = AdminRequest.objects.filter(user=request.user, status='Rejected').order_by('-created_at').first()
    
    if request.method == 'POST':
        if existing_request:
            messages.warning(request, 'You already have a pending request. Please wait for an admin to review it.')
            return redirect('dashboard')
            
        form = AdminRequestForm(request.POST)
        if form.is_valid():
            admin_req = form.save(commit=False)
            admin_req.user = request.user
            admin_req.save()
            messages.success(request, 'Your request to join the staff has been submitted for review.')
            return redirect('dashboard')
    else:
        form = AdminRequestForm()
        
    return render(request, 'accounts/request_to_admin.html', {
        'form': form,
        'has_pending': existing_request is not None,
        'last_rejected_request': last_rejected_request
    })


@login_required
def send_otp(request, otp_type):
    if otp_type not in ['Email', 'Phone']:
        messages.error(request, "Invalid OTP type.")
        return redirect('profile')

    # Delete any existing unused OTPs for this user and type
    OTPVerification.objects.filter(user=request.user, otp_type=otp_type, is_used=False).delete()

    # Generate a 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    OTPVerification.objects.create(
        user=request.user,
        otp_code=otp_code,
        otp_type=otp_type
    )

    # Simulated Sending
    target = request.user.email if otp_type == 'Email' else request.user.profile.phone
    print(f"\n[SIMULATED {otp_type.upper()} OTP] To: {target} | Code: {otp_code}\n")
    
    messages.success(request, f"A 6-digit OTP has been sent to your {otp_type.lower()}.")
    return redirect('verify-otp', otp_type=otp_type)


@login_required
def verify_otp(request, otp_type):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        # Find the latest unused OTP of this type
        otp_obj = OTPVerification.objects.filter(
            user=request.user, 
            otp_type=otp_type, 
            is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            messages.error(request, "No active OTP found. Please request a new one.")
            return redirect('profile')

        # Check for expiry (15 minutes)
        if timezone.now() > otp_obj.created_at + timedelta(minutes=15):
            otp_obj.is_used = True # Mark as "expired" effectively
            otp_obj.save()
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('profile')

        if otp_obj.otp_code == otp_code:
            otp_obj.is_used = True
            otp_obj.save()
            
            profile = request.user.profile
            if otp_type == 'Email':
                profile.is_email_verified = True
            else:
                profile.is_phone_verified = True
            profile.save()
            
            messages.success(request, f"Your {otp_type.lower()} has been verified successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify_otp.html', {'otp_type': otp_type})


@login_required
def verification_required(request):
    profile = request.user.profile
    if profile.is_phone_verified and profile.is_email_verified:
        return redirect('dashboard')
        
    return render(request, 'accounts/verification_required.html', {
        'profile': profile
    })
