# proyecto_web/middleware.py

from django.shortcuts import reverse
from django.urls import reverse, resolve
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    """
    Middleware que redirige a la página de inicio de sesión si el usuario no está autenticado
    y está intentando acceder a una URL protegida.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs protegidas
        # Usamos reverse, porque solo queremos obtener el nombre (name=) de las rutas
        rutas_protegidas = [
            reverse('principalUsuario'), # URLs que quieras proteger
            reverse('perfil'),
            reverse('carroCompra'),
            reverse('compra'),
        ]

        rutas_protegidas_admin = [
             reverse('vistaAdmin'),
             reverse('listarProducto'),
             reverse('crearOferta'),
             reverse('agregarCategoria'),
             reverse('agregarProductos'),
        ]

        match = resolve(request.path)
        # Verifica si la URL solicitada es una de las protegidas
        # Usamos redirect, porque genera una respuesta HTTP para evitar errores al redirigir al usuario
        
        if request.path in rutas_protegidas and not request.user.is_authenticated:
            # Si no está autenticado, redirige a la página de inicio de sesión
            return redirect('principal')
        elif request.path in rutas_protegidas and request.user.is_superuser:
            # Si es superusuario, redirige a otra página (puedes cambiar esta redirección)
            return redirect('vistaAdmin')
        elif request.path in rutas_protegidas_admin and not request.user.is_superuser:
            return redirect('principalUsuario')
        
        elif match.url_name == 'modificarProducto' and not request.user.is_superuser:
            return redirect('principalUsuario')
        
        response = self.get_response(request)
        return response
