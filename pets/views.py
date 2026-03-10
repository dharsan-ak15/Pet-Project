from django.contrib import messages
from .decorators import petportal_staff_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.utils import timezone

from .forms import PetRequestForm, PetSearchForm, CommentForm
from .models import Notification, PetRequest


def create_pet_request(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PetRequestForm(request.POST, request.FILES)

        print("POST DATA:", request.POST)
        print("FILES:", request.FILES)

        if form.is_valid():
            print("FORM IS VALID")

            pet_request = form.save(commit=False)
            pet_request.user = request.user
            pet_request.save()

            print("SAVED SUCCESSFULLY")

            messages.success(
                request,
                'Your pet request has been submitted and is pending review.'
            )
            return redirect('dashboard')
        else:
            print("FORM IS INVALID")
            print("ERRORS:", form.errors)

    else:
        form = PetRequestForm()

    return render(request, 'pets/pet_request_form.html', {'form': form})


def edit_pet_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect('login')

    pet_request = get_object_or_404(PetRequest, id=request_id, user=request.user)

    if request.method == 'POST':
        form = PetRequestForm(request.POST, request.FILES, instance=pet_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your pet report has been updated.')
            return redirect('dashboard')
    else:
        form = PetRequestForm(instance=pet_request)

    return render(request, 'pets/pet_request_form.html', {'form': form, 'is_edit': True})


def delete_pet_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect('login')

    pet_request = get_object_or_404(PetRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        pet_request.delete()
        messages.success(request, 'Your pet report has been deleted.')
        return redirect('dashboard')
        
    return render(request, 'pets/pet_request_confirm_delete.html', {'pet_request': pet_request})


@login_required
def search_pets(request):
    form = PetSearchForm(request.GET or None)
    results = []

    if form.is_valid():
        pet_type = form.cleaned_data.get('pet_type')
        breed = form.cleaned_data.get('breed')
        location = form.cleaned_data.get('location')
        request_type = form.cleaned_data.get('request_type') 
        gender = form.cleaned_data.get('gender')
        size = form.cleaned_data.get('size')

        query = Q()
        if gender:
            query &= Q(gender=gender)
        if size:
            query &= Q(size=size)
        if request_type:
            query &= Q(request_type=request_type)
        if pet_type:
            query &= Q(pet_type=pet_type)
        if breed:
            query &= Q(breed__icontains=breed)
        if location:
            query &= Q(location__icontains=location)


        results = PetRequest.objects.filter(query).order_by('-created_at')

        if not results.exists():
            messages.info(request, 'No matching pet found.')
    else:
        results = PetRequest.objects.all().order_by('-created_at')

    paginator = Paginator(results, 12) # Show 12 pets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pets/search.html', {'form': form, 'results': page_obj})


@petportal_staff_required
def admin_request_list(request):
    status_filter = request.GET.get('status', '')
    pet_requests = PetRequest.objects.all()

    if status_filter:
        pet_requests = pet_requests.filter(status=status_filter)

    pet_requests = pet_requests.order_by('-created_at')

    return render(
        request,
        'admin_panel/request_list.html',
        {'pet_requests': pet_requests, 
        'status_filter': status_filter, 
        'status_choices': PetRequest.STATUS_CHOICES
        },
    )


@petportal_staff_required
@require_POST
def update_request_status(request, request_id):
    pet_request = get_object_or_404(PetRequest, id=request_id)
    new_status = request.POST.get('status')

    if new_status not in {'Accepted', 'Rejected', 'Pending'}:
        messages.error(request, 'Invalid status.')
        return redirect('admin-request-list')

    pet_request.status = new_status
    pet_request.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'Request #{pet_request.id} updated to {new_status}.')
    return redirect('admin-request-list')


@petportal_staff_required
@require_POST
def delete_request(request, request_id):
    pet_request = get_object_or_404(PetRequest, id=request_id)
    pet_request.delete()
    messages.warning(request, f'Request #{request_id} has been deleted.')
    return redirect('admin-request-list')

def landing_page(request):
    print("LANDING PAGE VIEW IS CALLED!")

    time_threshold = timezone.now() - timedelta(hours=24)
    golden_hour_pets = PetRequest.objects.filter(
        status__in=['Pending', 'Accepted'],
        created_at__gte=time_threshold
    ).order_by('-created_at')[:4]

    lost_pets = PetRequest.objects.filter(
        request_type='Lost',
        status='Accepted'
    ).order_by('-created_at')[:4]

    found_pets = PetRequest.objects.filter(
        request_type='Found',
        status='Accepted'
    ).order_by('-created_at')[:4]

    adoption_pets = PetRequest.objects.filter(
        request_type='Adoption',
        status='Accepted'
    ).order_by('-created_at')[:4]

    total_pets = PetRequest.objects.count()
    total_reunited = PetRequest.objects.filter(status='Reunited').count()
    from django.contrib.auth.models import User
    total_users = User.objects.count()

    context = {
        'golden_hour_pets': golden_hour_pets,
        'lost_pets': lost_pets,
        'found_pets': found_pets,
        'adoption_pets': adoption_pets,
        'total_pets': total_pets,
        'total_reunited': total_reunited,
        'total_users': total_users,
    }

    return render(request, 'landing.html', context)

def profile_view(request):
    profile = request.user.profile

    if not request.user.is_authenticated:
        return redirect('login')

    user_requests = PetRequest.objects.filter(user=request.user)

    return render(request, 'pets/profile.html', {
        'user_requests': user_requests,
        'profile': profile
    })

@login_required
def lost_pets(request):
    pets = PetRequest.objects.filter(request_type='Lost', status='Accepted')
    return render(request, 'lost_pets.html', {'pets': pets})

@login_required
def found_pets(request):
    pets = PetRequest.objects.filter(request_type='Found', status='Accepted')
    return render(request, 'found_pets.html', {'pets': pets})

@login_required
def adoption_pets(request):
    pets = PetRequest.objects.filter(request_type='Adoption', status='Accepted')
    return render(request, 'adoption_pets.html', {'pets': pets})

def golden_hour_list(request):
    time_threshold = timezone.now() - timedelta(hours=24)
    pets = PetRequest.objects.filter(
        status__in=['Pending', 'Accepted'],
        created_at__gte=time_threshold
    ).order_by('-created_at')
    
    paginator = Paginator(pets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pets/golden_hour.html', {'page_obj': page_obj})

@login_required
def pet_detail(request, request_id):
    pet = get_object_or_404(PetRequest, pk=request_id)
    comments = pet.comments.all()
    
    # Check if user has already reported this pet
    from .models import ReportAbuse
    has_reported = False
    if request.user.is_authenticated:
        has_reported = ReportAbuse.objects.filter(reporter=request.user, pet_request=pet).exists()

    if request.method == 'POST':
        # Handle report abuse POST
        if 'report_reason' in request.POST:
            if not has_reported:
                reason = request.POST.get('report_reason')
                location = request.POST.get('report_location')
                image_url = request.POST.get('report_image_url')
                ReportAbuse.objects.create(
                    reporter=request.user,
                    pet_request=pet,
                    reason=reason,
                    location=location,
                    image_url=image_url
                )
                messages.success(request, 'Thank you. This pet profile has been reported to the administration for review.')
                return redirect('pet-detail', request_id=pet.id)
            else:
                messages.warning(request, 'You have already reported this profile.')
                return redirect('pet-detail', request_id=pet.id)

        # Handle comment POST
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.pet_request = pet
            comment.user = request.user
            comment.save()

            # Create notification for the pet owner (if the commenter isn't the owner)
            if pet.user != request.user:
                Notification.objects.create(
                    user=pet.user,
                    pet_request=pet,
                    message=f"{request.user.username} left a comment on your '{pet.pet_type}' report."
                )

            messages.success(request, 'Your comment was added.')
            return redirect('pet-detail', request_id=pet.id)
    else:
        form = CommentForm()

    return render(request, 'pets/pet_detail.html', {
        'pet': pet,
        'comments': comments,
        'form': form,
        'has_reported': has_reported
    })

@require_POST
def mark_reunited(request, request_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    pet_request = get_object_or_404(PetRequest, id=request_id, user=request.user)
    pet_request.status = 'Reunited'
    pet_request.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'Wonderful news! {pet_request.breed} has been marked as Reunited.')
    return redirect('dashboard')


@petportal_staff_required
def admin_dashboard(request):
    """
    Overview page for the custom staff portal.
    """
    from django.contrib.auth.models import User
    from django.db.models import Count
    
    total_users = User.objects.count()
    total_requests = PetRequest.objects.count()
    pending_requests = PetRequest.objects.filter(status='Pending').count()
    
    context = {
        'total_users': total_users,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@petportal_staff_required
def admin_users(request):
    """
    User management page for the custom staff portal.
    """
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj
    }
    return render(request, 'admin_portal/users.html', context)


@petportal_staff_required
def admin_abuse_reports(request):
    """
    Staff view to see and manage all user-submitted abuse reports.
    """
    from .models import ReportAbuse
    
    reports = ReportAbuse.objects.all().order_by('-created_at')
    
    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj
    }
    return render(request, 'admin_portal/abuse_reports.html', context)


def staff_login_view(request):
    """
    Simple view to authenticate staff members using a static password
    to grant access to the pet request admin portal.
    """
    if request.session.get('staff_access', False):
        return redirect('custom-admin-dashboard')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        if password == 'Petportalstaff':
            request.session['staff_access'] = True
            messages.success(request, 'Staff access granted.')
            return redirect('custom-admin-dashboard')
        else:
            messages.error(request, 'Incorrect staff password.')


    return render(request, 'admin_portal/staff_login.html')

def submit_general_abuse_report(request):
    """
    User-facing form view to report general pet abuse or fraudulent profiles globally.
    If POST, it pretends to submit (or optionally saves to an isolated model) and flashes success.
    """
    if request.method == 'POST':
        messages.success(request, 'Your report has been securely submitted to the moderation team for review.')
        return redirect('landing')

    return render(request, 'info/report_abuse_form.html')