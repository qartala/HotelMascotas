from django.urls import path
from .views import  cerrar_sesion_colaborador, eliminar_reserva, colaborador, iniciarsesionColaborador, registro_colaborador, eliminar_colaborador_aprobado, verificar_correo, verificar_usuario, inicio_colaborador, registrar_disponibilidad, perfil_colaborador, horas_disponibles


urlpatterns = [
    path('colaborador/',colaborador,name='colaborador'),
    path('iniciarsesionColaborador/',iniciarsesionColaborador,name='iniciarsesionColaborador'),
    path('registro_colaborador/', registro_colaborador, name='registro_colaborador'),
    path('cerrar_sesion_colaborador/', cerrar_sesion_colaborador, name='cerrar_sesion_colaborador'),
    
    path('eliminar_colaborador_aprobado/<int:colaborador_id>/', eliminar_colaborador_aprobado, name='eliminar_colaborador_aprobado'),
    path('verificar-correo/', verificar_correo, name='verificar_correo'),
    path('verificar-usuario/', verificar_usuario, name='verificar_usuario'),
    path('inicio_colaborador/', inicio_colaborador, name='inicio_colaborador'),
    path('disponibilidad/', registrar_disponibilidad, name='registrar_disponibilidad'),
    path('perfil_colaborador/', perfil_colaborador, name='perfil_colaborador'),
    path('horas_disponibles/', horas_disponibles, name='horas_disponibles'),
    path('eliminar-reserva/<int:reserva_id>/', eliminar_reserva, name='eliminar_reserva'),
]