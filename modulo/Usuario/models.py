from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Usuario(models.Model):
    idUsuario = models.OneToOneField(User,on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20)

class Suscripcion(models.Model):
    f_suscripcion=models.DateField()
    f_termino=models.DateField(null= True)
    monto=models.PositiveSmallIntegerField() 
    id_usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)