from django import template
from pets.models import PetRequest, ReportAbuse, PetContactRequest
from accounts.models import AdminRequest

register = template.Library()

@register.simple_tag
def get_pending_counts():
    return {
        'pet_reports': PetRequest.objects.filter(status='Pending').count(),
        'abuse_reports': ReportAbuse.objects.filter(status='Pending').count(),
        'contact_requests': PetContactRequest.objects.filter(status='Pending').count(),
        'admin_requests': AdminRequest.objects.filter(status='Pending').count() if hasattr(AdminRequest, 'objects') else 0,
    }
