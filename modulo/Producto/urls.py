from django.urls import path
from .views import dashboard_admin,listar_colaboradores_aprobados,solicitudes_admin, gestionar_solicitud,eliminar_membresia,editar_membresia,gestionar_membresias,crear_membresia,listar,admin, eliminar, agregarProductos, modificar, reservar_habitacion,obtener_reservas_json

urlpatterns = [
    path('dashboard_admin/',dashboard_admin, name='dashboard_admin'),
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
    
]
