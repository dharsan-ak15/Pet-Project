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

from .forms import CustomUserRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    pet_requests = PetRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')

    # ✅ SAFE for MySQL (no subquery update)
    for notification in unread_notifications:
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
    profile = request.user.profile
    # Only try to suggest if they have specified what they want or where they are
    if (profile.preferred_pet_type and profile.preferred_pet_type != 'None') or profile.city:
        query = Q(status='Accepted') & ~Q(user=request.user)
        if profile.preferred_pet_type and profile.preferred_pet_type != 'None':
            query &= Q(pet_type=profile.preferred_pet_type)
        if profile.city:
            query &= Q(location__icontains=profile.city)
        suggested_pets = PetRequest.objects.filter(query).order_by('-created_at')[:3]

    context = {
        'pet_requests': page_obj,
        'notifications': notifications,
        'suggested_pets': suggested_pets,
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
