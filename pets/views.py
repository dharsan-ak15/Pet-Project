from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PetRequestForm, PetSearchForm
from .models import PetRequest


def create_pet_request(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PetRequestForm(request.POST, request.FILES)

        print("POST DATA:", request.POST)
        print("FILES:", request.FILES)

        if form.is_valid():
            print("FORM IS VALID ✅")

            pet_request = form.save(commit=False)
            pet_request.user = request.user
            pet_request.save()

            print("SAVED SUCCESSFULLY ✅")

            messages.success(
                request,
                'Your pet request has been submitted and is pending review.'
            )
            return redirect('dashboard')
        else:
            print("FORM IS INVALID ❌")
            print("ERRORS:", form.errors)

    else:
        form = PetRequestForm()

    return render(request, 'pets/pet_request_form.html', {'form': form})

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

        results = PetRequest.objects.filter(query)

        if not results.exists():
            messages.info(request, 'No matching pet found.')

    return render(request, 'pets/search.html', {'form': form, 'results': results})


@staff_member_required
def admin_request_list(request):
    status_filter = request.GET.get('status', '')
    pet_requests = PetRequest.objects.all()

    if status_filter:
        pet_requests = pet_requests.filter(status=status_filter)

    paginator = Paginator(pet_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'admin_panel/request_list.html',
        {'page_obj': page_obj, 'status_filter': status_filter, 'status_choices': PetRequest.STATUS_CHOICES},
    )


@staff_member_required
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


@staff_member_required
@require_POST
def delete_request(request, request_id):
    pet_request = get_object_or_404(PetRequest, id=request_id)
    pet_request.delete()
    messages.warning(request, f'Request #{request_id} has been deleted.')
    return redirect('admin-request-list')

from pets.models import PetRequest

def landing_page(request):
    lost_pets = PetRequest.objects.filter(
        request_type='Lost',
        status='Accepted'
    ).order_by('-created_at')[:4]

    found_pets = PetRequest.objects.filter(
        request_type='Found',
        status='Accepted'
    ).order_by('-created_at')[:4]

    context = {
        'lost_pets': lost_pets,
        'found_pets': found_pets,
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

def lost_pets(request):
    pets = Pet.objects.filter(status='lost')
    return render(request, 'lost_pets.html', {'pets': pets})

def found_pets(request):
    pets = Pet.objects.filter(status='found')
    return render(request, 'found_pets.html', {'pets': pets})