from django.db import models
from modulo.Usuario.models import Ficha
from django.contrib.auth.models import User
from django.db.models import Q
import datetime

def generar_nombre_unico(instancia, archivo):
    extension_archivo = archivo.split('.')[-1]
    nombre_unico = datetime.datetime.now()
    return f"{nombre_unico}.{extension_archivo}" 

# class Categoria(models.Model):
#     nombre = models.CharField(max_length=30)

# class Promocion(models.Model):
#     porc_descuento = models.PositiveSmallIntegerField()
#     f_inicio = models.DateField()
#     f_termino = models.DateField()
#     nombre = models.CharField(max_length=30, default='o')

class Habitacion(models.Model):
    imagen_habitacion = models.FileField(upload_to=generar_nombre_unico, null=False, default=0)
    numero_habitacion = models.CharField(max_length=10, unique=True)
    tipo_habitacion = models.CharField(max_length=200)
    precio = models.PositiveSmallIntegerField()
    # servicio = models.CharField(max_length=200)
    # tiempoText = models.CharField(max_length=200)
    # id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    # id_Promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE)

class Reserva(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_total = models.PositiveIntegerField()  

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