from django.urls import path
from .views import listar,admin, eliminar, agregarProductos, modificar

urlpatterns = [
    path('panel/',admin, name='vistaAdmin'),
    # path('promociones/', promociones, name='promociones'),
    path('agregarProductos/', agregarProductos, name='agregarProductos'),
    # path('crearOferta/', crearOferta, name='crearOferta'),
    # path('agregarCategoria/', agregarCategoria, name='agregarCategoria'),
    path('Productos/', listar, name='listarProducto'),
    path('modificar/<int:idHabitacion>/', modificar, name='modificarProducto'),  
    path('eliminar/<int:idProducto>/', eliminar, name='eliminarProducto'),
]
