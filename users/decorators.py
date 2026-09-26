from functools import wraps
from typing import Any, Callable

from django.core.exceptions import PermissionDenied
#
#
# def role_required(*roles: object) -> Callable[..., Callable[..., Any]]:
#     def decorator(view_func):
#         @wraps(view_func)
#         def wrapper(request, *args, **kwargs):
#             print('DEBUG: user =', request.user, '| role =', getattr(request.user, 'role', 'НЕТ АТРИБУТА'),
#                   '| roles needed =', roles)
#             if request.user.role not in roles:
#                 raise PermissionDenied
#             return view_func(request, *args, **kwargs)
#
#         return wrapper
#
#     return decorator

from functools import wraps
from typing import Any, Callable

from django.core.exceptions import PermissionDenied


def role_required(*roles) -> Callable:

    # нормализуем роли в строки
    allowed = {r.value if hasattr(r, 'value') else str(r) for r in roles}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            user_role = getattr(request.user, 'role', None)
            if user_role not in allowed:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
