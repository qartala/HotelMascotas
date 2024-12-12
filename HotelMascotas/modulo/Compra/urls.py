from django.urls import path
from .views import iniciar_pago, pago_exitoso, iniciar_pago_regalos, pago_exitoso_regalos

urlpatterns = [
    path('pagar/<int:item_id>/<str:tipo_pago>/', iniciar_pago, name='iniciar_pago'),
    path('pago-exitoso/<str:tipo_pago>/', pago_exitoso, name='pago_exitoso'),
    path('iniciar-pago-regalos/<int:reserva_id>/', iniciar_pago_regalos, name='iniciar_pago_regalos'),
    path('pago-exitoso-regalos/<int:reserva_id>/', pago_exitoso_regalos, name='pago_exitoso_regalos'),
]