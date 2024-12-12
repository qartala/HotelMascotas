from django.db import models
from django.contrib.auth.models import User
from modulo.Colaborador.models import Colaborador
from django.apps import apps
from modulo.Producto.models import Reserva , ReservaRegalia
from django.db.models.signals import post_save, post_delete  # Importa las señales que necesites
from django.dispatch import receiver  # Importa el decorador receiver
import datetime




class Usuario(models.Model):
    idUsuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20)
    membresia = models.ForeignKey(
        'Producto.Membresia', on_delete=models.SET_NULL, null=True, blank=True
    )
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    trabajador = models.BooleanField(default=False)
    fecha_inicio_membresia = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.idUsuario.username} - {'Trabajador' if self.trabajador else 'Usuario'}"
    
    def tiene_membresia_activa(self):
        print(f"Verificando membresía para el usuario: {self.idUsuario.username}")
        if not self.fecha_inicio_membresia:
            print("El usuario no tiene una membresía activa.")
            return False
        is_active = self.fecha_inicio_membresia <= datetime.date.today()
        print(f"Membresía activa: {is_active}")
        return is_active



class Ficha(models.Model):
    nombre_perro = models.CharField(max_length=100)
    nombre_dueno = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    edad = models.IntegerField()
    peso = models.FloatField()
    chip = models.CharField(max_length=10)
    comida = models.CharField(max_length=100)
    vacunas = models.TextField()
    alergias = models.TextField()
    enfermedades = models.TextField()
    imagen_mascota = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_perro

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
    cancelada = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['colaborador', 'servicio', 'fecha_reservada', 'hora_inicio', 'hora_fin'],
                condition=models.Q(cancelada=False), 
                name='unique_reserva_activa'
            )
        ]

    def __str__(self):
        return f"Reserva de {self.mascota.nombre_perro} para el servicio {self.servicio} el {self.fecha_reservada}"

    

class Calificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.PositiveSmallIntegerField(default=5) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    revisada = models.BooleanField(default=False) 
    def __str__(self):
        return f"{self.usuario.username}: {self.calificacion} estrellas"
    
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)



class ServiciosComunes(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name='servicios_comunes')
    reserva = models.ForeignKey('Producto.Reserva', on_delete=models.CASCADE, related_name='servicios_comunes', null=True, blank=True)
    dia = models.PositiveIntegerField() 
    comio = models.BooleanField(default=False)
    paseo = models.BooleanField(default=False)
    entretencion = models.BooleanField(default=False)
    medicamentos = models.BooleanField(default=False)
    fecha_registro = models.DateField()  
    observacion = models.TextField(blank=True, null=True) 
    
    regalo_evidencia =  models.ImageField(upload_to='evidencias/regalo/', blank=True, null=True)
    comio_evidencia = models.ImageField(upload_to='evidencias/comio/', blank=True, null=True)
    paseo_evidencia = models.ImageField(upload_to='evidencias/paseo/', blank=True, null=True)
    entretencion_evidencia = models.ImageField(upload_to='evidencias/entretencion/', blank=True, null=True)
    medicamentos_evidencia = models.ImageField(upload_to='evidencias/medicamentos/', blank=True, null=True)

    def __str__(self):
        return f"Servicios para {self.ficha.nombre_perro} - Día {self.dia}"

class Mensaje(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="mensajes")
    emisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mensajes_enviados")
    receptor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mensajes_recibidos")
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.emisor.username} a {self.receptor.username}"
    

