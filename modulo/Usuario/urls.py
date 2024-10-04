from django.urls import path
from .views import colaborador
from . import views
from django.conf import settings
from django.conf.urls.static import static


from .views import eliminar_reserva,horas_reservadas,perfil_colaborador,registrar_disponibilidad,principal,eliminar_ficha,editar_ficha_view,listar_fichas_view,ficha_salud_view,perfil,verificar_usuario,verificar_correo,listar_colaboradores_aprobados,iniciarsesionColaborador,eliminar_suscriptor,suscripcion,desuscribirse,registrarse,iniciarsesion,eliminarSuscriptor,ingresarSuscriptor,vigencia,principalUsuario,listar,cerrar_sesion

urlpatterns = [
    path('',principal,name='principal'),
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
    path('colaborador/',colaborador,name='colaborador'),
    path('iniciarsesionColaborador/',iniciarsesionColaborador,name='iniciarsesionColaborador'),
    path('registro/', views.registro_colaborador, name='registro_colaborador'),
    path('solicitudes/', views.solicitudes_admin, name='solicitudes_admin'),
    path('gestionar_solicitud/<int:colaborador_id>/<str:accion>/', views.gestionar_solicitud, name='gestionar_solicitud'),
    path('colaboradores_aprobados', listar_colaboradores_aprobados, name='listar_colaboradores_aprobados'),
    path('eliminar_colaborador_aprobado/<int:colaborador_id>/', views.eliminar_colaborador_aprobado, name='eliminar_colaborador_aprobado'),
    path('verificar-correo/', verificar_correo, name='verificar_correo'),
    path('verificar-usuario/', verificar_usuario, name='verificar_usuario'),
    path('ficha-salud/',ficha_salud_view, name='ficha_salud'),
    path('listar-fichas/',listar_fichas_view, name='listar_fichas'),
    path('editar-ficha/<int:pk>/', editar_ficha_view, name='editar_ficha'),
    path('eliminar-ficha/<int:id>/', eliminar_ficha, name='eliminar_ficha'),
    path('perfil/',perfil, name='perfil'),
    path('inicio_colaborador/', views.inicio_colaborador, name='inicio_colaborador'),
    path('iniciarsesionColaborador/', views.iniciarsesionColaborador, name='iniciarsesionColaborador'),
    path('disponibilidad/', registrar_disponibilidad, name='registrar_disponibilidad'),
    path('perfil_colaborador/', views.perfil_colaborador, name='perfil_colaborador'),
    path('horas_reservadas/', horas_reservadas, name='horas_reservadas'),
    path('eliminar-reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


