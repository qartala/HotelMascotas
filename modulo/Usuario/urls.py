from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views import (
    agregar_calificacion, mostrar_calificacion, enviar_calificacion, 
    actualizar_perfil, cancelar_membresia, cambiar_membresia, 
    gestionar_membresia_usuario, unirse_membresia, prueba, 
    eliminar_reserva_servicio, listar_reservas_servicios, reservar_servicio, 
    ver_horas_colaborador, servicios_disponibles, eliminar_reserva_habitacion, 
    generar_pdf_fichas, reservas_hotel, listar_reservas_view, principal, 
    eliminar_ficha, editar_ficha_view, listar_fichas_view, ficha_salud_view, 
    perfil, registrarse, iniciarsesion, principalUsuario, cerrar_sesion,listar_calificaciones,
    contacto
)

urlpatterns = [
    path('', principal, name='principal'),  # Página principal
    path('registrarse/', registrarse, name='registrarse'),
    path('iniciarsesion/', iniciarsesion, name='iniciarsesion'),
    path('cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),
    path('principalUsuario/', principalUsuario, name='principalUsuario'),

    path('perfil/', perfil, name='perfil'),
    path('actualizar-perfil/', actualizar_perfil, name='actualizar_perfil'),
    path('ficha-salud/', ficha_salud_view, name='ficha_salud'),
    path('listar-fichas/', listar_fichas_view, name='listar_fichas'),
    path('editar-ficha/<int:pk>/', editar_ficha_view, name='editar_ficha'),
    path('eliminar-ficha/<int:id>/', eliminar_ficha, name='eliminar_ficha'),
    path('descargar-fichas/', generar_pdf_fichas, name='descargar_fichas'),

    path('listar-reservas/', listar_reservas_view, name='listar_reservas'),
    path('reservas/eliminar/<int:reserva_id>/', eliminar_reserva_habitacion, name='eliminar_reserva_habitacion'),
    path('reservas_hotel/<int:habitacion_id>/', reservas_hotel, name='reservas_hotel'),

    path('servicios-disponibles/', servicios_disponibles, name='servicios_disponibles'),
    path('ver-horas-colaborador/<int:colaborador_id>/', ver_horas_colaborador, name='ver_horas_colaborador'),
    path('reservar_servicio/', reservar_servicio, name='reservar_servicio'),
    path('listar-reservas-servicios/', listar_reservas_servicios, name='listar_reservas_servicios'),
    path('eliminar-reserva-servicio/<int:reserva_id>/', eliminar_reserva_servicio, name='eliminar_reserva_servicio'),

    path('unirse-membresia/<int:membresia_id>/', unirse_membresia, name='unirse_membresia'),
    path('gestionar-membresia/', gestionar_membresia_usuario, name='gestionar_membresia_usuario'),
    path('cambiar-membresia/', cambiar_membresia, name='cambiar_membresia'),
    path('cancelar-membresia/', cancelar_membresia, name='cancelar_membresia'),

    path('agregar-calificacion/', agregar_calificacion, name='agregar_calificacion'),
    path('mostrar-calificacion/', mostrar_calificacion, name='mostrar_calificacion'),  
    path('enviar-calificacion/', enviar_calificacion, name='enviar_calificacion'),
    path('eliminar-calificacion/<int:calificacion_id>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    path('', listar_calificaciones, name='inicio_cliente'),
    path('contacto/', contacto, name='contacto'),

    path('prueba/', prueba, name='prueba'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
