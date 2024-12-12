from django.urls import path
from .views import (
    ReservaList, ReservaDetail,
    UsuarioList, UsuarioDetail,
    FichaList, FichaDetail  ,ficha_mascota,
    HabitacionList, HabitacionDetail,
    RegaliaList, RegaliaDetail,MembresiaList,MembresiaDetail,
    api_login,check_in_view,actualizar_check_in,actualizar_pagado,  perfil_view,listar_seguimiento_servicios_comunes,
    ServiciosComunesDetailView,ServiciosComunesListCreateView,ServiciosComunesView,
    SubirEvidenciaView, historial_chat ,enviar_mensaje,CrearReservaRegalia,
    ReservaRegaliaList,ReservaRegaliaDetail,
    SubirVideoAPIView,EliminarVideoAPIView,ListarVideosReservaAPIView,EstadoMembresiaAPIView,
    ListarTodasReservasAPIView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', api_login, name='api_login'),
    #Rutas para iniciar sesion
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rutas para Reserva
    path('reservas/', ReservaList.as_view(), name='reserva-list'),
    path('reservas/<int:pk>/', ReservaDetail.as_view(), name='reserva-detail'),

    # Rutas para Usuario
    path('usuarios/', UsuarioList.as_view(), name='usuario-list'),
    path('usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detail'),

    # Rutas para Ficha
    path('fichas/', FichaList.as_view(), name='ficha-list'),
    path('fichas/<int:pk>/', FichaDetail.as_view(), name='ficha-detail'),

    # Rutas para Habitacion
    path('habitaciones/', HabitacionList.as_view(), name='habitacion-list'),
    path('habitaciones/<int:pk>/', HabitacionDetail.as_view(), name='habitacion-detail'),

    path('reserva/<int:reserva_id>/check-in/', check_in_view, name='api_check_in'),
    
    #CheckIn
    path('reservas/<int:id>/check-in/',actualizar_check_in, name='reserva_detail'), 
    #pago
    path('reservas/<int:id>/pagado/', actualizar_pagado, name='actualizar_pagado'),

   
    path('ficha-mascota/<int:reserva_id>/', ficha_mascota, name='ficha_mascota'),
    
    path('servicios/', ServiciosComunesListCreateView.as_view(), name='servicios-list-create'),
    path('servicios/<int:pk>/', ServiciosComunesDetailView.as_view(), name='servicios-detail'),
    
    path('servicios-comunes/<int:id_ficha>/<int:id_reserva>/', ServiciosComunesView.as_view(), name='servicios-comunes'),
         
    path('servicios-comunes/<int:pk>/subir-evidencia/<str:campo>/', SubirEvidenciaView.as_view(), name='subir-evidencia'),
    
    # Rutas de API REST
    # Historial de chat
    path('chat/history/<int:reserva_id>/', historial_chat, name='historial_chat'),
    
    # Enviar mensaje
    path('chat/enviar/', enviar_mensaje, name='enviar_mensaje'),
    
    path('perfil/', perfil_view, name='perfil_view'),

    path('membresia/', MembresiaList.as_view(), name='membresia-list-create'),
    path('membresia/<int:pk>/', MembresiaDetail.as_view(), name='membresia-detail'),

    path('seguimiento/servicios/<int:reserva_id>/', listar_seguimiento_servicios_comunes, name='listar_seguimiento_servicios_comunes'),
    
    path('regalias/', RegaliaList.as_view(), name='regalia-list'),
    path('regalias/<int:pk>/', RegaliaDetail.as_view(), name='regalia-detail'),

    path('reservaregalia/', ReservaRegaliaList.as_view(), name='reserva_r-list'),
    path('reservaregalia/<int:pk>/', ReservaRegaliaDetail.as_view(), name='reserva_r-detail'),

    path('reservaregalia1/', CrearReservaRegalia.as_view(), name='crear_reserva_regalia'),
    
    # Subir videos
    path('videos/subir/', SubirVideoAPIView.as_view(), name='subir-video'),
    
    # Eliminar videos
    path('videos/<int:video_id>/eliminar/', EliminarVideoAPIView.as_view(), name='eliminar-video'),
    
    
    path('videos/reserva/<int:reserva_id>/', ListarVideosReservaAPIView.as_view(), name='listar-videos'),
    
    path('usuarios/membresia/estado/', EstadoMembresiaAPIView.as_view(), name='estado-membresia'),



   
]







    
