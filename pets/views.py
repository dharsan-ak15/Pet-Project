from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
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
            
            # Combine district and area into location
            district = form.cleaned_data.get('district')
            area = form.cleaned_data.get('area')
            pet_request.location = f"{area}, {district}"
            
            # Staff reports are auto-approved (direct listing)
            if request.user.is_staff:
                pet_request.status = 'Accepted'
            
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
            updated_pet = form.save(commit=False)
            district = form.cleaned_data.get('district')
            area = form.cleaned_data.get('area')
            updated_pet.location = f"{area}, {district}"
            # Maintain staff auto-approval on edit
            if request.user.is_staff and updated_pet.status == 'Pending':
                updated_pet.status = 'Accepted'
            updated_pet.save()
            messages.success(request, 'Your pet report has been updated.')
            return redirect('dashboard')
    else:
        # Pre-fill custom form fields from the generated location string
        initial_data = {}
        if pet_request.location:
            parts = pet_request.location.rsplit(", ", 1)
            if len(parts) == 2:
                initial_data['area'] = parts[0]
                initial_data['district'] = parts[1]
            else:
                initial_data['area'] = pet_request.location
                
        form = PetRequestForm(instance=pet_request, initial=initial_data)

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
        district = form.cleaned_data.get('district')
        area = form.cleaned_data.get('area')
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
        if breed:
            query &= Q(breed__icontains=breed)
        if district:
            query &= Q(location__icontains=district)
        if area:
            query &= Q(location__icontains=area)


        results = PetRequest.objects.filter(query, status='Accepted').order_by('-created_at')

        if not results.exists():
            messages.info(request, 'No matching pet found.')
    else:
        results = PetRequest.objects.filter(status='Accepted').order_by('-created_at')

    paginator = Paginator(results, 1000) # Show all pets in one page (effectively no pagination)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pets/search.html', {'form': form, 'results': page_obj})


@staff_member_required
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


@staff_member_required
@require_POST
def update_request_status(request, request_id):
    from .models import Notification
    pet_request = get_object_or_404(PetRequest, id=request_id)
    new_status = request.POST.get('status')

    if new_status not in {'Accepted', 'Rejected', 'Pending'}:
        messages.error(request, 'Invalid status.')
        return redirect('admin-request-list')

    pet_request.status = new_status
    
    if new_status == 'Rejected':
        rejection_reason = request.POST.get('rejection_reason', '')
        pet_request.rejection_reason = rejection_reason
        pet_request.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        
        # Create notification for the user
        Notification.objects.create(
            user=pet_request.user,
            pet_request=pet_request,
            message=f"Your pet report for '{pet_request.breed}' was declined. Reason: {rejection_reason}"
        )
    else:
        pet_request.save(update_fields=['status', 'updated_at'])
        # Create notification for the user
        Notification.objects.create(
            user=pet_request.user,
            pet_request=pet_request,
            message=f"Your pet report for '{pet_request.breed}' was accepted! It is now visible to the community."
        )
        messages.success(request, f'Request #{pet_request.id} updated to {new_status}.')
        
    return redirect('admin-request-list')


@staff_member_required
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
    ).exclude(request_type='Adoption').order_by('-created_at')[:4]

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
    ).exclude(request_type='Adoption').order_by('-created_at')
    
    paginator = Paginator(pets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pets/golden_hour.html', {'page_obj': page_obj})

@login_required
def pet_detail(request, request_id):
    pet = get_object_or_404(PetRequest, pk=request_id)
    comments = pet.comments.all()
    
    # Check if user has already reported this pet
    from .models import ReportAbuse, PetContactRequest
    from .forms import ContactRequestForm
    
    has_reported = False
    contact_request_status = None
    has_contact_access = False
    
    if request.user.is_authenticated:
        has_reported = ReportAbuse.objects.filter(reporter=request.user, pet_request=pet).exists()
        
        # Check contact request status
        contact_request = PetContactRequest.objects.filter(requester=request.user, pet=pet).first()
        if contact_request:
            contact_request_status = contact_request.status

        if pet.user == request.user or request.user.is_staff or contact_request_status == 'Approved':
            has_contact_access = True

    if request.method == 'POST':
        # Handle report abuse POST
        if 'reason' in request.POST and 'submit_abuse_report' in request.POST:
            if not has_reported:
                abuse_form = AbuseReportForm(request.POST, request.FILES)
                if abuse_form.is_valid():
                    abuse_report = abuse_form.save(commit=False)
                    abuse_report.reporter = request.user
                    abuse_report.pet_request = pet
                    abuse_report.save()
                    messages.success(request, 'Thank you. This pet profile has been reported to the administration for review.')
                else:
                    messages.error(request, 'There was an error in your report. Please check the fields.')
                return redirect('pet-detail', request_id=pet.id)
            else:
                messages.warning(request, 'You have already reported this profile.')
                return redirect('pet-detail', request_id=pet.id)

        # Handle Contact Request
        if 'submit_contact_request' in request.POST:
            contact_form = ContactRequestForm(request.POST, request.FILES)
            if contact_form.is_valid():
                if not contact_request_status: # Prevent duplicate requests
                    contact_request = contact_form.save(commit=False)
                    contact_request.requester = request.user
                    contact_request.pet = pet
                    contact_request.save()
                    messages.success(request, 'Your contact request has been submitted to moderators for approval.')
                else:
                    messages.warning(request, 'You have already submitted a request for this pet.')
                return redirect('pet-detail', request_id=pet.id)

        # Handle comment POST
        if 'content' in request.POST:
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
        contact_form = ContactRequestForm()

    return render(request, 'pets/pet_detail.html', {
        'pet': pet,
        'comments': comments,
        'form': form,
        'contact_form': contact_form,
        'has_reported': has_reported,
        'contact_request_status': contact_request_status,
        'has_contact_access': has_contact_access
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


# ---------------------------------------------------------
# Custom Staff Portal Views (Now standard /staff/)
# ---------------------------------------------------------

@staff_member_required
def admin_dashboard(request):
    """
    Overview page for the custom staff portal.
    """
    from django.contrib.auth.models import User
    from django.db.models import Count
    from .models import PetContactRequest
    
    total_users = User.objects.count()
    total_requests = PetRequest.objects.count()
    pending_requests = PetRequest.objects.filter(status='Pending').count()
    pending_contact_requests = PetContactRequest.objects.filter(status='Pending').count()
    
    context = {
        'total_users': total_users,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'pending_contact_requests': pending_contact_requests,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@staff_member_required
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


@staff_member_required
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


@staff_member_required
@require_POST
def admin_delete_user(request, user_id):
    from django.contrib.auth.models import User
    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete.is_superuser:
        messages.error(request, 'Cannot delete superuser accounts.')
    else:
        user_to_delete.delete()
        messages.success(request, f'User {user_to_delete.username} has been successfully deleted.')
    return redirect('custom-admin-users')


@staff_member_required
def admin_contact_requests(request):
    """
    Staff view to see and manage all user-submitted contact access requests.
    """
    from .models import PetContactRequest
    
    contact_requests = PetContactRequest.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        contact_requests = contact_requests.filter(status=status_filter)
    
    paginator = Paginator(contact_requests, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contact_requests': page_obj,
        'status_filter': status_filter
    }
    return render(request, 'admin_portal/contact_requests.html', context)

@staff_member_required
@require_POST
def update_contact_request_status(request, request_id):
    from .models import PetContactRequest, Notification
    contact_request = get_object_or_404(PetContactRequest, id=request_id)
    new_status = request.POST.get('status')
    
    if new_status not in {'Approved', 'Rejected', 'Pending'}:
        messages.error(request, 'Invalid status update.')
        return redirect('admin-contact-requests')
        
    contact_request.status = new_status
    contact_request.save(update_fields=['status'])
    
    if new_status == 'Approved':
        Notification.objects.create(
            user=contact_request.requester,
            pet_request=contact_request.pet,
            message=f"Your contact request was approved. You can now contact the pet owner for '{contact_request.pet.breed}'."
        )
        Notification.objects.create(
            user=contact_request.pet.user,
            pet_request=contact_request.pet,
            message=f"You have a new approved contact request from {contact_request.requester.username} for '{contact_request.pet.breed}'."
        )
        messages.success(request, f"Granted contact access to {contact_request.requester.username}.")
    elif new_status == 'Rejected':
        rejection_reason = request.POST.get('rejection_reason', '')
        contact_request.rejection_reason = rejection_reason
        contact_request.save(update_fields=['rejection_reason'])
        
        reason_text = f" Reason: {rejection_reason}" if rejection_reason else ""
        Notification.objects.create(
            user=contact_request.requester,
            pet_request=contact_request.pet,
            message=f"Your request was declined by staff for '{contact_request.pet.breed}'.{reason_text}"
        )
        
    return redirect('admin-contact-requests')

def submit_general_abuse_report(request):
    """
    User-facing form view to report general pet abuse or fraudulent profiles globally.
    """
    from .forms import AbuseReportForm
    if request.method == 'POST':
        form = AbuseReportForm(request.POST, request.FILES)
        if form.is_valid():
            abuse_report = form.save(commit=False)
            if request.user.is_authenticated:
                abuse_report.reporter = request.user
            abuse_report.save()
            messages.success(request, 'Your report has been securely submitted to the moderation team for review.')
            return redirect('landing')
    else:
        form = AbuseReportForm()

    return render(request, 'info/report_abuse_form.html', {'form': form})

@staff_member_required
def admin_admin_requests(request):
    """
    Staff view to see and manage all user-submitted requests to become an Admin/Staff.
    """
    from accounts.models import AdminRequest
    
    admin_requests = AdminRequest.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        admin_requests = admin_requests.filter(status=status_filter)
    
    paginator = Paginator(admin_requests, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'admin_requests': page_obj,
        'status_filter': status_filter
    }
    return render(request, 'admin_portal/admin_requests.html', context)


@staff_member_required
@require_POST
def update_admin_request_status(request, request_id):
    from accounts.models import AdminRequest
    
    admin_request = get_object_or_404(AdminRequest, id=request_id)
    new_status = request.POST.get('status')
    
    if new_status not in {'Approved', 'Rejected', 'Pending'}:
        messages.error(request, 'Invalid status update.')
        return redirect('admin-admin-requests')
        
    admin_request.status = new_status
    admin_request.save(update_fields=['status'])
    
    # Process the approval/rejection
    if new_status == 'Approved':
        # Make the user a staff member
        user = admin_request.user
        user.is_staff = True
        user.save(update_fields=['is_staff'])
        
        from pets.models import Notification
        Notification.objects.create(
            user=user,
            message="Congratulations! Your request to join the staff has been approved. You now have access to the Staff Portal.",
            pet_request=None
        )
        messages.success(request, f"Request approved. {user.username} is now a Staff member.")
    elif new_status == 'Rejected':
        rejection_reason = request.POST.get('rejection_reason', '')
        admin_request.rejection_reason = rejection_reason
        admin_request.save(update_fields=['rejection_reason'])
        
        from pets.models import Notification
        reason_text = f" Reason: {rejection_reason}" if rejection_reason else ""
        Notification.objects.create(
            user=admin_request.user,
            message=f"Your request to join the staff was declined.{reason_text}",
            pet_request=None
        )
        
    return redirect('admin-admin-requests')

@login_required
@require_POST
def submit_complaint(request):
    from accounts.models import SystemComplaint
    
    complaint_text = request.POST.get('complaint_text')
    
    if not complaint_text:
        messages.error(request, "Complaint text cannot be empty.")
        return redirect(request.META.get('HTTP_REFERER', 'landing'))
        
    SystemComplaint.objects.create(
        user=request.user,
        complaint_text=complaint_text
    )
    
    messages.success(request, "Your complaint has been submitted. Admin will review it shortly.")
    return redirect(request.META.get('HTTP_REFERER', 'landing'))

@staff_member_required
def admin_system_complaints(request):
    from accounts.models import SystemComplaint
    
    complaints = SystemComplaint.objects.all().order_by('-created_at')
    
    context = {
        'complaints': complaints
    }
    return render(request, 'admin_portal/system_complaints.html', context)

