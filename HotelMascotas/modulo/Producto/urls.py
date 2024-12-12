from django.urls import path
from .views import listar_calificaciones_bajas, marcar_calificacion_revisada, reservas_activas,marcar_como_pagada, realizar_check_in,iniciar_pago,dashboard_operativo,dashboard_estrategico,modificar_trabajador,eliminar_trabajador,listar_trabajadores, realizar_checkout, recepcion,registrar_trabajador,listar_reservas_admin,eliminar_regalia,modificar_regalia,agregar_regalia,listar_regalias,dashboard_admin,listar_colaboradores_aprobados, responder_calificacion,solicitudes_admin, gestionar_solicitud,eliminar_membresia,editar_membresia,gestionar_membresias,crear_membresia,listar,admin, eliminar, agregarProductos, modificar, reservar_habitacion,obtener_reservas_json

urlpatterns = [
    path('dashboard_admin/',dashboard_admin, name='dashboard_admin'),
    path('dashboard_operativo/',dashboard_operativo, name='dashboard_operativo'),
    path('dashboard_estrategico/',dashboard_estrategico, name='dashboard_estrategico'),

    path('agregarProductos/', agregarProductos, name='agregarProductos'),
    path('Productos/', listar, name='listarProducto'),
    path('modificar/<int:idHabitacion>/', modificar, name='modificarProducto'),  
    path('eliminar/<int:idProducto>/', eliminar, name='eliminarProducto'),

    path('crear-membresia/', crear_membresia, name='crear_membresia'),
    path('gestionar-membresias/', gestionar_membresias, name='gestionar_membresias'),
    path('editar-membresia/<int:membresia_id>/', editar_membresia, name='editar_membresia'),
    path('eliminar-membresia/<int:membresia_id>/', eliminar_membresia, name='eliminar_membresia'),

    path('solicitudes/', solicitudes_admin, name='solicitudes_admin'),
    path('gestionar_solicitud/<int:colaborador_id>/<str:accion>/', gestionar_solicitud, name='gestionar_solicitud'),
    path('colaboradores_aprobados', listar_colaboradores_aprobados, name='listar_colaboradores_aprobados'),

    path('reservar_habitacion/<int:habitacion_id>/', reservar_habitacion, name='reservar_habitacion'),
    path('obtener_reservas_json/<int:habitacion_id>/', obtener_reservas_json, name='obtener_reservas_json'),

    path('registro-trabajador/', registrar_trabajador, name='registro_trabajador'),
    path('trabajadores/', listar_trabajadores, name='listar_trabajadores'),
    path('eliminar-trabajador/<int:id>/', eliminar_trabajador, name='eliminar_trabajador'),
    path('modificar-trabajador/<int:id>/', modificar_trabajador, name='modificar_trabajador'),

    path('regalias/', listar_regalias, name='listar_regalias'),
    path('agregar-regalia/', agregar_regalia, name='agregar_regalia'),
    path('modificar-regalia/<int:regalia_id>/', modificar_regalia, name='modificar_regalia'),
    path('eliminar-regalia/<int:regalia_id>/', eliminar_regalia, name='eliminar_regalia'),

    path('listar_reservas_admin/',listar_reservas_admin,name='listar_reservas_admin'),
    path('admin/reservas-activas/', reservas_activas, name='reservas_activas'),
    
    path('iniciar_pago/<int:membresia_id>/<str:tipo>/', iniciar_pago, name='iniciar_pago'),
    path('checkin/<int:reserva_id>/', realizar_check_in, name='realizar_check_in'),
    path('realizar_checkout/<int:id>/', realizar_checkout, name='realizar_checkout'),
    path('recepcion/', recepcion, name='recepcion'),
    path('realizar_checkout/<int:reserva_id>/', realizar_checkout, name='realizar_checkout'),
    path('marcar-como-pagada/<int:reserva_id>/', marcar_como_pagada, name='marcar_como_pagada'),
    path('responder/<int:calificacion_id>/', responder_calificacion, name='responder_calificacion'),
    path("calificaciones-bajas/", listar_calificaciones_bajas, name="listar_calificaciones_bajas"),
    path('marcar-revisada/<int:calificacion_id>/', marcar_calificacion_revisada, name='marcar_calificacion_revisada'),
]







