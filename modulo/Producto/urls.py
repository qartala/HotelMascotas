from django.urls import path
from django.contrib.auth import views as auth_views
from .views import listar, eliminar, principal, promociones, agregarProductos, crearOferta, agregarCategoria, modificar

urlpatterns = [
    path('', principal, name='principal'),
    path('', auth_views.LoginView.as_view(), name=''),
    path('promociones/', promociones, name='promociones'),
    path('agregarProductos/', agregarProductos, name='agregarProductos'),
    path('crearOferta/', crearOferta, name='crearOferta'),
    path('agregarCategoria/', agregarCategoria, name='agregarCategoria'),
    path('Productos/', listar, name='listarProducto'),
    path('modificar/<int:idHabitacion>/', modificar, name='modificarProducto'),  # Cambiado aquí
    path('eliminar/<int:idProducto>/', eliminar, name='eliminarProducto'),
]
