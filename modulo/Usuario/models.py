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

class Ficha(models.Model):
    nombre_perro = models.CharField(max_length=100)
    nombre_dueno = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    edad = models.IntegerField()
    peso = models.FloatField()
    chip = models.CharField(max_length=10)  # 'si' o 'no'
    comida = models.CharField(max_length=100)
    vacunas = models.TextField()
    alergias = models.TextField()
    enfermedades = models.TextField()
    id_usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)

    def str(self):
        return f"{self.nombre_perro} ({self.nombre_dueno})"