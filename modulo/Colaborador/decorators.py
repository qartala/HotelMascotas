from django.shortcuts import redirect
from django.urls import reverse

def colaborador_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Verificar si el colaborador está en la sesión
        if 'colaborador_id' not in request.session:
            # Redirigir al inicio de sesión si no está autenticado
            return redirect(reverse('colaborador'))
        return view_func(request, *args, **kwargs)
    return wrapper

def colaborador_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        colaborador_id = request.session.get('colaborador_id')
        if not colaborador_id:
            return redirect('iniciarsesionColaborador')
        return view_func(request, *args, **kwargs)
    return wrapper