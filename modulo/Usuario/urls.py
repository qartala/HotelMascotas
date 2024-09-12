from django.urls import path
from .views import eliminar_suscriptor,admin,suscripcion,desuscribirse,registrarse,iniciarsesion,admin,eliminarSuscriptor,ingresarSuscriptor,vigencia,principalUsuario,listar,cerrar_sesion

urlpatterns = [
    path('',admin,name='vistaAdmin'),
    path('suscripcion',suscripcion,name='suscripcion'),
    path('desuscribirse',desuscribirse,name='desuscribirse'),
    path('registrarse',registrarse,name = 'registrarse'),
    path('iniciarsesion',iniciarsesion,name='iniciarsesion'),
    path('eliminarsuscriptor/<int:usuario>',eliminarSuscriptor,name='eliminarSuscriptor'),
    path('ingresarSuscriptor',ingresarSuscriptor,name='ingresarSuscriptor'),
    path('vigencia',vigencia,name='vigencia'),
    path('principalUsuario', principalUsuario, name='principalUsuario'),
    path('listarUsuario',listar,name='listarUsuario'),
    path('cerrar_sesion',cerrar_sesion,name='cerrar_sesion'),
    path('eliminar_suscriptor/<int:id_s>',eliminar_suscriptor,name='eliminar_suscriptor'),
    
]


