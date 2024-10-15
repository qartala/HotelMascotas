from django.urls import path
from .views import iniciar_pago, pago_exitoso

urlpatterns = [
    path('pagar/<int:item_id>/<str:tipo_pago>/', iniciar_pago, name='iniciar_pago'),
    path('pago-exitoso/<str:tipo_pago>/', pago_exitoso, name='pago_exitoso'),
]