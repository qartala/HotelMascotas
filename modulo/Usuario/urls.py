from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import reservas_hotel,listar_reservas_view,principal,eliminar_ficha,editar_ficha_view,listar_fichas_view,ficha_salud_view,perfil,registrarse,iniciarsesion,principalUsuario,cerrar_sesion

urlpatterns = [
    path('',principal,name='principal'),
    path('registrarse',registrarse,name = 'registrarse'),
    path('iniciarsesion',iniciarsesion,name='iniciarsesion'),
    path('principalUsuario', principalUsuario, name='principalUsuario'),
    path('perfil/',perfil, name='perfil'),
    path('cerrar_sesion',cerrar_sesion,name='cerrar_sesion'),
    path('ficha-salud/',ficha_salud_view, name='ficha_salud'),
    path('listar-fichas/',listar_fichas_view, name='listar_fichas'),
    path('editar-ficha/<int:pk>/', editar_ficha_view, name='editar_ficha'),
    path('eliminar-ficha/<int:id>/', eliminar_ficha, name='eliminar_ficha'),
    path('listar-reservas/',listar_reservas_view, name='listar_reservas'),
    path('reservas_hotel/', reservas_hotel, name='reservas_hotel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

