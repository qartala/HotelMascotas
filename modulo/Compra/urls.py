from django.urls import path,include
from .views import  agregar_carrito, agregar_carrito2, carroCompra,histoCompra,seguimiento,compra
from .views import eliminar_producto ,vaciarCarro ,mas,menos,realizar_compra

urlpatterns = [
    path('carroCompra',carroCompra,name='carroCompra'),
    path('agregar/<int:producto_id>',agregar_carrito,name='agregar'),
    path('agregar2/<int:habitacion_id>/', agregar_carrito2, name='agregar2'),
    path('eliminar/<int:carrito_id>',eliminar_producto,name='eliminar'),
    path('histoCompra', histoCompra,name='histoCompra'),
    path('seguimiento', seguimiento,name='seguimiento'),
    path('compra', compra ,name='compra'),
    path('Vaciar', vaciarCarro ,name='vaciar'),
    path('mas/<int:id_p>', mas,name='mas'),
    path('menos/<int:id_p>', menos,name='menos'),
    path('Realizar', realizar_compra ,name='Realizar'),
]
    
