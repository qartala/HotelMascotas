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
            'registrar_disponibilidad',
            'perfil_colaborador',
            'horas_disponibles',
            'cerrar_sesion_colaborador',
            'horas_disponibles',
            'eliminar_reserva',
            'prueba'
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
            'eliminar',
            'reservar_habitacion',
            'listar_reservas',
            'obtener_reservas_json',
            'reservas_hotel',
            'descargar_fichas',
            'iniciar_pago',
            'pago_exitoso',
            'eliminar_reserva_habitacion',
            'servicios_disponibles',
            'horas_disponibles',
            'ver_horas_colaborador',
            'reservar_servicio',
            'listar_reservas_servicios',
            'eliminar_reserva_servicio',
            'unirse_membresia',
            'gestionar_membresia_usuario',
            'cambiar_membresia',
            'cancelar_membresia',
            'actualizar_perfil',
            'agregar_calificacion',
            'mostrar_calificacion',
            'enviar_calificacion',
            'eliminar_calificacion',
            'inicio_cliente',
            'generar_pdf_reserva'
        ]

        rutas_protegidas_admin = [
             'vistaAdmin',
             'dashboard_admin',
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
             'gestionar_solicitud',
             'crear_membresia',
             'gestionar_membresias',
             'editar_membresia',
             'eliminar_membresia',
        ]

        if request.path.startswith('/media/'):
            return self.get_response(request)
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
