from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import datetime


class Membresia(models.Model):
    nombre = models.CharField(max_length=50)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    duracion_dias = models.PositiveIntegerField()  # Duración en días (mensual, trimestral, anual)
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Valor de la membresía

    def str(self):
        return self.nombre

def generar_nombre_unico(instancia, archivo):
    extension_archivo = archivo.split('.')[-1]
    nombre_unico = datetime.datetime.now()
    return f"{nombre_unico}.{extension_archivo}" 
    
class Habitacion(models.Model):
    imagen_habitacion = models.FileField(upload_to=generar_nombre_unico, null=False, default=0)
    numero_habitacion = models.CharField(max_length=10, unique=True)
    tipo_habitacion = models.CharField(max_length=200)
    precio = models.PositiveSmallIntegerField()

class Reserva(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    mascota = models.ForeignKey('Usuario.Ficha', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_total = models.PositiveIntegerField()  
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva de {self.cliente.username} en la habitación {self.habitacion.numero_habitacion}"

    def calcular_precio_total(self):
        # Calcular la diferencia de días entre fecha_fin y fecha_inicio
        dias_reserva = (self.fecha_fin - self.fecha_inicio).days
        return dias_reserva * self.habitacion.precio
    
    def verificar_disponibilidad(habitacion, fecha_inicio, fecha_fin):
    # Filtrar reservas que se solapen con las fechas solicitadas
        reservas_conflictivas = Reserva.objects.filter(
            habitacion=habitacion
        ).filter(
            Q(fecha_inicio__lte=fecha_fin) & Q(fecha_fin__gte=fecha_inicio)
        )

        if reservas_conflictivas.exists():
            return False  # No está disponible
        return True  # Disponible