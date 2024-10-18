from django.db import models
from django.contrib.auth.models import User
from modulo.Colaborador.models import Colaborador
from django.apps import apps


# Create your models here.
    
class Usuario(models.Model):
    idUsuario = models.OneToOneField(User,on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20)
    membresia = models.ForeignKey('Producto.Membresia', on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

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
    imagen_mascota = models.ImageField(upload_to='', blank=True, null=True)
    id_usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)

    def str(self):
        return f"{self.nombre_perro}"
    
    #listar mascota y dueno
    # def str(self):
    #     return f"{self.nombre_perro} ({self.nombre_dueno})"
    
    def get_vacunas(self):
        return self.vacunas.split(',')

    def get_alergias(self):
        return self.alergias.split(',')

    def get_enfermedades(self):
        return self.enfermedades.split(',')
    
class ReservaServicio(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=100)
    fecha_reservada = models.DateField()
    mascota = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    precio = models.PositiveIntegerField()
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('colaborador', 'servicio', 'fecha_reservada', 'hora_inicio', 'hora_fin', 'mascota')

    def str(self):
        return f"Reserva de {self.mascota.nombre_perro} para el servicio {self.servicio} el {self.fecha_reservada}"

class Calificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.PositiveSmallIntegerField(default=5)  # Default definido aquí
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username}: {self.calificacion} estrellas"
