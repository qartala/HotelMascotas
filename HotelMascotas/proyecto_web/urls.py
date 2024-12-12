from django.contrib import admin
from django.urls import path,include
from django.conf import global_settings as settings 
from django.conf.urls import static
from django.conf import settings
from django.conf.urls.static import static
from modulo.Usuario.urls import urlpatterns as urlusuario
from modulo.Compra.urls import urlpatterns as urlcompra
from modulo.Producto.urls import urlpatterns as urlhabitacion
from modulo.Colaborador.urls import urlpatterns as urlcolaborador
from modulo.API.urls import urlpatterns as urlAPI

urlpatterns = [
    path('', include(urlusuario)),
    path('admin/',include(urlhabitacion)),
    path('compra/',include(urlcompra)),
    path('colaborador/',include(urlcolaborador)),
    path('api/', include(urlAPI))
    #path('habitacion/',include(urlhabitacion))
]


# Configuración para servir archivos estáticos y media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    
  