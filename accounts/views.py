from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from pets.models import Notification, PetRequest

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .forms import CustomUserRegisterForm

def register(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Save profile image
            profile = user.profile
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
                profile.save()

            return redirect('login')
    else:
        form = CustomUserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

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

    context = {
        'pet_requests': pet_requests,
        'notifications': notifications,
    }

    return render(request, 'accounts/dashboard.html', context)
