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
        rutas_protegidas_sin_sesion = [
            'principal',
            'iniciarsesion',
            'registrarse',
            'colaborador',
            'registro_colaborador',
            'iniciarsesionColaborador',
            'inicio_colaborador',
            'iniciarsesionColaborador',
            'registrar_disponibilidad',
            'perfil_colaborador',
            'horas_reservadas'
        ]
         
        rutas_protegidas = [
            'principalUsuario', # URLs que quieras proteger
            'perfil',
            'carroCompra',
            'compra',
            'cerrar_sesion',
            'ficha_salud',
            'listar_fichas',
            'editar_ficha',
            'eliminar_ficha',
            'carroCompra',
            'agregar',
            'agregar2',
            'eliminar',
            'histoCompra',
            'seguimiento',
            'compra',
            'vaciar',
            'mas',
            'menos',
            'iniciar_pago',
            'confirmar_pago',
            'Realizar'
        ]

        rutas_protegidas_admin = [
             'vistaAdmin',
             'listarProducto',
             'crearOferta',
             'agregarCategoria',
             'solicitudes_admin',
             'listar_colaboradores_aprobados',
             'agregarProductos',
             'modificarProducto',
             'eliminarProducto',
             'cerrar_sesion',
             'verificar_usuario',
             'verificar_correo',
             'eliminar_colaborador_aprobado',
             'gestionar_solicitud'
        ]

        # Verifica si la URL solicitada es una de las protegidas
        # Usamos redirect, porque genera una respuesta HTTP para evitar errores al redirigir al usuario
        ruta_actual = resolve(request.path_info).url_name

        if not request.user.is_authenticated:
            if ruta_actual not in rutas_protegidas_sin_sesion:
                # Redirigir a una página pública o de inicio de sesión si no está autenticado
                return redirect(reverse('iniciarsesion'))

        # Caso 2: Usuario autenticado y no es admin
        elif request.user.is_authenticated and not request.user.is_staff:
            if ruta_actual not in rutas_protegidas:
                # Redirigir al perfil de usuario si intenta acceder a una ruta no autorizada
                return redirect(reverse('principalUsuario'))

        # Caso 3: Usuario autenticado y es admin
        elif request.user.is_authenticated and request.user.is_staff:
            if ruta_actual not in rutas_protegidas_admin:
                # Redirigir al panel de admin si intenta acceder a una ruta no autorizada
                return redirect(reverse('vistaAdmin'))
        
        response = self.get_response(request)
        return response
