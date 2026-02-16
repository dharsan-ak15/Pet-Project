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
        if form.is_valid():
            pet_request = form.save(commit=False)
            pet_request.user = request.user
            pet_request.save()
            messages.success(request, 'Your pet request has been submitted and is pending review.')
            return redirect('dashboard')
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

        query = Q(status='Accepted')
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
