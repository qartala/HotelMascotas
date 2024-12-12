from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views import regalos,eliminar_enfermedades,eliminar_alergias,eliminar_vacunas,modificar_mascota,generar_pdf_reserva,listar_calificaciones,eliminar_calificacion,enviar_calificacion,mostrar_calificacion,agregar_calificacion,actualizar_perfil,cancelar_membresia,cambiar_membresia,gestionar_membresia_usuario,unirse_membresia,prueba,eliminar_reserva_servicio,listar_reservas_servicios,reservar_servicio,ver_horas_colaborador,servicios_disponibles, eliminar_reserva_habitacion,generar_pdf_fichas, reservas_hotel,listar_reservas_view,principal,eliminar_ficha,editar_ficha_view,listar_fichas_view,ficha_salud_view,perfil,registrarse,iniciarsesion,principalUsuario,cerrar_sesion

urlpatterns = [
    path('',principal,name='principal'),
    path('registrarse',registrarse,name = 'registrarse'),
    path('iniciarsesion',iniciarsesion,name='iniciarsesion'),
    path('cerrar_sesion',cerrar_sesion,name='cerrar_sesion'),
    path('principalUsuario', principalUsuario, name='principalUsuario'),

    path('perfil/',perfil, name='perfil'),
    path('regalos/', regalos, name='regalos'),
    path('actualizar-perfil/',actualizar_perfil, name='actualizar_perfil'),
    path('ficha-salud/',ficha_salud_view, name='ficha_salud'),
    path('listar-fichas/',listar_fichas_view, name='listar_fichas'),
    path('editar-ficha/<int:pk>/', editar_ficha_view, name='editar_ficha'),
    path('modificar-mascota/<int:id_mascota>/', modificar_mascota, name='modificar_mascota'),
    path('eliminar-ficha/<int:id>/', eliminar_ficha, name='eliminar_ficha'),
    path('descargar-fichas/',generar_pdf_fichas, name='descargar_fichas'),
    path('eliminar_vacunas/<int:id>/',eliminar_vacunas, name='eliminar_vacunas'),
    path('eliminar_alergias/<int:id>/',eliminar_alergias, name='eliminar_alergias'),
    path('eliminar_enfermedades/<int:id>/',eliminar_enfermedades, name='eliminar_enfermedades'),

    path('listar-reservas/',listar_reservas_view, name='listar_reservas'),
    path('reservas/eliminar/<int:reserva_id>/', eliminar_reserva_habitacion, name='eliminar_reserva_habitacion'),
    path('reserva/pdf/<int:reserva_id>/', generar_pdf_reserva, name='generar_pdf_reserva'),
    path('reservas_hotel/<int:habitacion_id>/', reservas_hotel, name='reservas_hotel'),

    path('servicios-disponibles/', servicios_disponibles, name='servicios_disponibles'),
    path('ver-horas-colaborador/<int:colaborador_id>/', ver_horas_colaborador, name='ver_horas_colaborador'),
    path('reservar_servicio/', reservar_servicio, name='reservar_servicio'),
    path('listar-reservas-servicios/',listar_reservas_servicios, name='listar_reservas_servicios'),
    path('eliminar-reserva-servicio/<int:reserva_id>/',eliminar_reserva_servicio, name='eliminar_reserva_servicio'),

    path('unirse-membresia/<int:membresia_id>/', unirse_membresia, name='unirse_membresia'),
    path('gestionar-membresia/',gestionar_membresia_usuario, name='gestionar_membresia_usuario'),
    path('cambiar-membresia/', cambiar_membresia, name='cambiar_membresia'),
    path('cancelar-membresia/', cancelar_membresia, name='cancelar_membresia'),

    path('agregar-calificacion/', agregar_calificacion, name='agregar_calificacion'),
    path('mostrar-calificacion/', mostrar_calificacion, name='mostrar_calificacion'),  
    path('enviar-calificacion/', enviar_calificacion, name='enviar_calificacion'),
    path('eliminar-calificacion/<int:calificacion_id>/', eliminar_calificacion, name='eliminar_calificacion'),
    path('', listar_calificaciones, name='inicio_cliente'),
    
    

    path('prueba/',prueba, name='prueba'),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

