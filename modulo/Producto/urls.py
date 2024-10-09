from django.urls import path
from .views import listar,admin, eliminar, agregarProductos, modificar, reservar_habitacion,obtener_reservas_json, reservas_hotel

urlpatterns = [
    path('panel/',admin, name='vistaAdmin'),
    # path('promociones/', promociones, name='promociones'),
    path('agregarProductos/', agregarProductos, name='agregarProductos'),
    # path('crearOferta/', crearOferta, name='crearOferta'),
    # path('agregarCategoria/', agregarCategoria, name='agregarCategoria'),
    path('Productos/', listar, name='listarProducto'),
    path('modificar/<int:idHabitacion>/', modificar, name='modificarProducto'),  
    path('eliminar/<int:idProducto>/', eliminar, name='eliminarProducto'),
    path('reservar_habitacion/<int:habitacion_id>/', reservar_habitacion, name='reservar_habitacion'),
    path('obtener_reservas_json/', obtener_reservas_json, name='obtener_reservas_json'),
    path('reservas_hotel/', reservas_hotel, name='reservas_hotel')
]
