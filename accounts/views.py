from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from pets.models import Notification, PetRequest


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    pet_requests = PetRequest.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    Notification.objects.filter(id__in=unread_notifications.values_list('id', flat=True)).update(is_read=True)

    context = {
        'pet_requests': pet_requests,
        'notifications': unread_notifications,
    }
    return render(request, 'accounts/dashboard.html', context)
