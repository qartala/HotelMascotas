from django.urls import path
from .views import iniciar_pago, pago_exitoso

urlpatterns = [
    path('pagar/<int:reserva_id>/<str:tipo_reserva>/', iniciar_pago, name='iniciar_pago'),
    path('pago-exitoso/<str:tipo_reserva>/', pago_exitoso, name='pago_exitoso'),
]