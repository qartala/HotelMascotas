from django.db import models
import datetime

def generar_nombre_unico(instancia, archivo):
    extension_archivo = archivo.split('.')[-1]
    nombre_unico = datetime.datetime.now()
    return f"{nombre_unico}.{extension_archivo}" 

class Categoria(models.Model):
    nombre = models.CharField(max_length=30)

class Promocion(models.Model):
    porc_descuento = models.PositiveSmallIntegerField()
    f_inicio = models.DateField()
    f_termino = models.DateField()
    nombre = models.CharField(max_length=30, default='o')

class Habitacion(models.Model):
    imagen = models.FileField(upload_to=generar_nombre_unico, null=False, default=0)
    tipoPerro = models.CharField(max_length=200)
    kilos = models.CharField(max_length=200)
    servicio = models.CharField(max_length=200)
    precio = models.PositiveSmallIntegerField()
    tiempoText = models.CharField(max_length=200)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    id_Promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE)
