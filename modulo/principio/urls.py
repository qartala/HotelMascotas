from django.urls import path
from .views import principal,principalUsuario

urlpatterns = [
    path('', principal, name='principal'),
   
]