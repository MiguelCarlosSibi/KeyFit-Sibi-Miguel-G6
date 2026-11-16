from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
