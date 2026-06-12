from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def manager_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_manager:
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped
