from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def petportal_staff_required(view_func):
    """
    Decorator for views that checks that the user has entered the
    master 'Petportalstaff' password in their session.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('staff_access', False):
            messages.warning(request, "Restricted area. Please enter the staff password.")
            return redirect('custom-admin-login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
