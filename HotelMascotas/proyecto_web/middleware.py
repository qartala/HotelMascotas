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
            'reserva-list',
            'reserva-detail',
            'usuario-list',
            'usuario-detail',
            'ficha-list',
            'ficha-detail',
            'habitacion-list',
            'habitacion-detail',
            'api_login',
            'prueba',
            'api_check_in',
            'reserva-list',
            'reserva_detail',
            'actualizar_pagado',
            'regalia-list',
            'regalia-detail',
            'servicios-list-create',
            'servicios-detail',
            'servicios-comunes',
            'subir-evidencia',
            'perfil_view',
            'historial_chat',
            'enviar_mensaje',
            'asignar_trabajador',
            'membresia-list-create',
            'membresia-detail',
            'get_reservas',
            'listar_seguimiento_servicios_comunes',
            'mensajes_no_leidos',
            'marcar_mensajes_leidos',
            'reserva_r-list',
            'reserva_r-detail',
            'crear_reserva_regalia',
            'subir-video',
            'eliminar-video',
            'listar-videos',
            'estado-membresia'

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
            'generar_pdf_reserva',
            'api_login',
            'api_check_in',
            'reserva-list',
            'reserva_detail',
            'actualizar_pagado',
            'regalia-list',
            'regalia-detail',
            'servicios-list-create',
            'servicios-detail',
            'servicios-comunes',
            'modificar_mascota',
            'subir-evidencia',
            'perfil_view',
            'eliminar_vacunas',
            'eliminar_alergias',
            'eliminar_enfermedades',
            'historial_chat',
            'enviar_mensaje',
            'asignar_trabajador',
            'membresia-list-create',
            'membresia-detail',
            'get_reservas',
            'listar_seguimiento_servicios_comunes',
            'mensajes_no_leidos',
            'marcar_mensajes_leidos',
            'reserva_r-list',
            'reserva_r-detail',
            'crear_reserva_regalia',
            'regalos',
            'iniciar_pago_regalos',
            'pago_exitoso_regalos',
            'subir-video',
            'eliminar-video',
            'listar-videos',
            'estado-membresia'
 
        
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
             'api_login',
             'registro_trabajador',
             'eliminar_trabajador',
             'listar_trabajadores',
             'modificar_trabajador',
             'api_check_in',
             'reserva-list',
             'listar_regalias',
             'agregar_regalia',
             'modificar_regalia',
             'eliminar_regalia',
             'listar_reservas_admin',
             'reserva_detail',
             'actualizar_pagado',
             'regalia-list',
             'regalia-detail',
             'servicios-list-create',
             'servicios-detail',
             'servicios-comunes',
             'dashboard_estrategico',
             'dashboard_operativo',
             'subir-evidencia',
             'perfil_view',
             'realizar_check_in',
             'realizar_checkout',
             'recepcion',
             'marcar_como_pagada',
             'historial_chat',
             'enviar_mensaje',
             'asignar_trabajador',
             'membresia-list-create',
             'membresia-detail',
             'get_reservas',
             'listar_seguimiento_servicios_comunes',
             'mensajes_no_leidos',
             'marcar_mensajes_leidos',
             'reserva_r-list',
             'reserva_r-detail',
             'crear_reserva_regalia',
             'reservas_activas',
             'subir-video',
            'eliminar-video',
            'listar-videos',
            'estado-membresia',
            'responder_calificacion',
            'listar_calificaciones_bajas',
            'marcar_calificacion_revisada',
    
        
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
                return redirect(reverse('dashboard_admin'))
        
        response = self.get_response(request)
        return response
