from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Q
import datetime
from django.db import transaction


class Video(models.Model):
    cliente = models.ForeignKey('Usuario.Usuario', on_delete=models.CASCADE, related_name='videos')
    reserva = models.ForeignKey('Producto.Reserva', on_delete=models.CASCADE, related_name='videos_reserva')
    ficha = models.ForeignKey('Usuario.Ficha', on_delete=models.CASCADE, related_name='videos_mascota')
    archivo_video = models.FileField(upload_to='videos_clientes/', verbose_name="Archivo de Video")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Video de {self.cliente.idUsuario.username} para la reserva {self.reserva.id} - Mascota: {self.ficha.nombre_perro}"


class Membresia(models.Model):
    nombre = models.CharField(max_length=50)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    duracion_dias = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


def generar_nombre_unico(instancia, archivo):
    extension_archivo = archivo.split('.')[-1]
    nombre_unico = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{nombre_unico}.{extension_archivo}"


class Habitacion(models.Model):
    imagen_habitacion = models.FileField(upload_to=generar_nombre_unico, null=False, default=0)
    numero_habitacion = models.CharField(max_length=10, unique=True)
    tipo_habitacion = models.CharField(max_length=200)
    
    precio = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Habitación {self.numero_habitacion}"


class Reserva(models.Model):
    habitacion = models.ForeignKey('Habitacion', on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_cliente')
    trabajador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_trabajador'
    )  # Relación con el trabajador
    mascota = models.ForeignKey('Usuario.Ficha', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_total = models.PositiveBigIntegerField()
    pagado = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    check_in = models.BooleanField(default=False)
    checkout = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva de {self.cliente.username} en la habitación {self.habitacion.numero_habitacion}"

    @staticmethod
    def verificar_disponibilidad(habitacion, fecha_inicio, fecha_fin):
        """
        Verifica si la habitación está disponible para las fechas dadas.
        """
        reservas_conflictivas = Reserva.objects.filter(
            habitacion=habitacion,
            cancelada=False
        ).filter(
            Q(fecha_inicio__lte=fecha_fin) & Q(fecha_fin__gte=fecha_inicio)
        )
        return not reservas_conflictivas.exists()
 
    def calcular_precio_total(self):
        """
        Calcula el precio total de la reserva basado en los días reservados y el precio de la habitación.
        """
        dias_reserva = (self.fecha_fin - self.fecha_inicio).days
        return max(1, dias_reserva) * self.habitacion.precio

    @transaction.atomic
    def realizar_checkout(self):
        """
        Marca el checkout de la reserva y libera las fechas de la habitación.
        """
        if self.check_in and not self.checkout:
            self.checkout = True
            self.save()

            # Lógica para liberar fechas en el sistema de disponibilidad (si existe)
            print(f"Checkout realizado para la reserva {self.id}")



class Regalia(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Regalía")
    foto = models.ImageField(upload_to='regalias/', verbose_name="Foto de la Regalía")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.PositiveIntegerField(verbose_name="Precio (CLP)")
    stock = models.PositiveIntegerField(verbose_name="Stock disponible")

    def __str__(self):
        return self.nombre

    def reducir_stock(self, cantidad):
        """
        Disminuye el stock si hay suficiente disponible.
        """
        if cantidad <= self.stock:
            self.stock -= cantidad
            self.save()
        else:
            raise ValueError("No hay suficiente stock disponible.")



class ReservaRegalia(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    reserva = models.ForeignKey(
        'Reserva', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='regalias'
    ) 
    regalia = models.ForeignKey(
        'Regalia', on_delete=models.CASCADE, related_name='reservas_regalia'
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_total_r = models.PositiveBigIntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    pagada = models.BooleanField(default=False)
    usada = models.BooleanField(default=False,null=True)
    
    def __str__(self):
        return f"{self.cantidad} x {self.regalia.nombre} para la reserva {self.reserva.id}"

    @property
    def precio_total(self):
        """Calcula el precio total basado en el precio de la regalia y la cantidad."""
        if hasattr(self.regalia, 'precio'):  # Asegúrate de que 'precio' exista en el modelo Regalia
            return self.regalia.precio * self.cantidad
        return 0
