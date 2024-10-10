from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class Colaborador(models.Model):
    fullname = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    servicio = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='pdf_colaboradores/')
    password = models.CharField(max_length=255)  # Almacenar contraseñas encriptadas
    descripcion = models.TextField(null=True, blank=True)  # Nuevo campo de descripción
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)  # Campo para la foto de perfil

    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

    def set_password(self, raw_password):
        """Cifra la contraseña usando la utilidad make_password de Django."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Verifica la contraseña usando la utilidad check_password de Django."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username


class Disponibilidad(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=100)  # Registrar el servicio
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = ('colaborador', 'servicio', 'fecha', 'hora_inicio')

    def __str__(self):
        return f"{self.colaborador.fullname} ({self.servicio}) - {self.fecha} de {self.hora_inicio} a {self.hora_fin}"