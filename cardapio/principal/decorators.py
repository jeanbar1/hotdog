from django.shortcuts import redirect
from django.contrib import messages

def group_required(group_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Você não tem permissão para acessar esta página.")
                return redirect("home")
        return _wrapped_view
    return decorator