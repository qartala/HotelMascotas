from django.urls import path
from .views import listar,admin, eliminar,promociones, agregarProductos, crearOferta, agregarCategoria, modificar

urlpatterns = [
    path('panel/',admin, name='vistaAdmin'),
    path('promociones/', promociones, name='promociones'),
    path('agregarProductos/', agregarProductos, name='agregarProductos'),
    path('crearOferta/', crearOferta, name='crearOferta'),
    path('agregarCategoria/', agregarCategoria, name='agregarCategoria'),
    path('Productos/', listar, name='listarProducto'),
    path('modificar/<int:idHabitacion>/', modificar, name='modificarProducto'),  # Cambiado aquí
    path('eliminar/<int:idProducto>/', eliminar, name='eliminarProducto'),
]
