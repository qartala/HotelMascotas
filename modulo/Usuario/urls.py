from django.urls import path
from .views import colaborador
from .views import principal,eliminar_ficha,editar_ficha_view,listar_fichas_view,ficha_salud_view,perfil,eliminar_suscriptor,suscripcion,desuscribirse,registrarse,iniciarsesion,eliminarSuscriptor,ingresarSuscriptor,vigencia,principalUsuario,listar,cerrar_sesion

urlpatterns = [
    path('principal', principal, name='principal'),
    path('suscripcion',suscripcion,name='suscripcion'),
    path('perfil/', perfil, name='perfil'),
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
    path('colaborador/',colaborador,name='colaborador'),
    path('ficha-salud/',ficha_salud_view, name='ficha_salud'),
    path('listar-fichas/',listar_fichas_view, name='listar_fichas'),
    path('editar-ficha/<int:pk>/', editar_ficha_view, name='editar_ficha'),
    path('eliminar-ficha/<int:id>/', eliminar_ficha, name='eliminar_ficha')
]


