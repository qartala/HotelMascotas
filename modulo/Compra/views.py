import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from modulo.Compra.models import Carrito, Detalle_compra ,Habitacion, Historial,Seguimiento,Compra
from modulo.Usuario.models import Usuario

# Create your views here.
def carroCompra(request):
    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    carrito = Carrito.objects.filter(idUsuario__id = usuario.id)
    
    total = 0
    for x in carrito:
        total += x.total
    contexto = {
        'carrito':carrito,
        'total':total
    }
    return render(request,'base/carro_compra.html',contexto)

def vaciarCarro(request):
    cliente = Usuario.objects.get(idUsuario = request.user.id)
    CarritoCliente = Carrito.objects.filter(idUsuario = cliente.id)
    CarritoCliente.delete()
    return HttpResponseRedirect(reverse('carroCompra'))



def agregar_carrito(request,habitacion_id ):
    productoEncontrado = Habitacion.objects.get(id = habitacion_id)
    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    
    try:
        producto_carrito = Carrito.objects.get(idProducto__id = productoEncontrado.id,idUsuario__id = usuario.id)
        print(producto_carrito)
        producto_carrito.cantidad = producto_carrito.cantidad + 1 
        producto_carrito.total = producto_carrito.cantidad * producto_carrito.idProducto.precio
        producto_carrito.save()

    except Exception:

        nuevocarrito = Carrito()
        nuevocarrito.cantidad = 1
        nuevocarrito.total =productoEncontrado.precio * nuevocarrito.cantidad
        nuevocarrito.idProducto = productoEncontrado
        nuevocarrito.idUsuario = usuario
        nuevocarrito.save()
    return HttpResponseRedirect(reverse('promociones'))

@login_required
def agregar_carrito2(request, habitacion_id):
    productoEncontrado = Habitacion.objects.get(id=habitacion_id)
    usuario = Usuario.objects.get(idUsuario=request.user.id)

    try:
        producto_carrito = Carrito.objects.get(idProducto=productoEncontrado, idUsuario=usuario)
        producto_carrito.cantidad += 1
        producto_carrito.total = producto_carrito.cantidad * producto_carrito.idProducto.precio
        producto_carrito.save()
    except Carrito.DoesNotExist:
        nuevocarrito = Carrito()
        nuevocarrito.cantidad = 1
        nuevocarrito.total = productoEncontrado.precio
        nuevocarrito.idProducto = productoEncontrado
        nuevocarrito.idUsuario = usuario
        nuevocarrito.save()

    return redirect('principalUsuario')




def eliminar_producto(request, carrito_id):
    carrito = Carrito.objects.get(id = carrito_id)
    carrito.delete()
    return HttpResponseRedirect(reverse('carroCompra'))




def dCompra(request,idDetalle_Compra):
    
    carritoe = Carrito.objects.get(id = idDetalle_Compra)
    contexto = {
        'carrito':carritoe
    }
    if request.method == 'POST':
        carritoe.delete()
        return HttpResponseRedirect(reverse('carroCompra'))
    return render(request,'base/carro_compra.html',contexto)


def histoCompra(request):

    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    historia = Historial.objects.filter(idUsuario__id = usuario.id)
    
    contexto = {
        
        'historial':historia
    }
    return render(request,'base/historial_comp.html',contexto)

def seguimiento(request):
    return render(request,'base/seguimiento_comp.html')

def compra (request):
    cliente = Usuario.objects.get(idUsuario = request.user.id)
    carrito = Carrito.objects.filter(idUsuario__id =cliente.id)
    total = 0
    for x in carrito:
        total += x.total
    contexto = {
        'cliente':cliente,
        'carrito':carrito,
        'total':total,
    }
   
    
    return render (request,'base/compra.html',contexto)

def mas(request,id_p):
    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    producto_carrito = Carrito.objects.get(idProducto__id=id_p,idUsuario__id = usuario.id)
    producto_carrito.cantidad =producto_carrito.cantidad + 1 
    producto_carrito.total = producto_carrito.cantidad * producto_carrito.idProducto.precio
    producto_carrito.save()
    return HttpResponseRedirect (reverse('carroCompra'))

def menos(request,id_p):
    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    producto_carrito = Carrito.objects.get(idProducto__id=id_p,idUsuario__id = usuario.id)
    producto_carrito.cantidad =producto_carrito.cantidad - 1 
    producto_carrito.total = producto_carrito.cantidad * producto_carrito.idProducto.precio
    if producto_carrito.cantidad == 0:
        producto_carrito.delete()
    else:
        producto_carrito.save()
    return HttpResponseRedirect (reverse('carroCompra'))

def realizar_compra(request):
    usuario = Usuario.objects.get(idUsuario__id =request.user.id )
    carrito = Carrito.objects.filter(idUsuario__id = usuario.id)
    #compra = Historial()
    compra = Compra()
    seguimiento = Seguimiento()
    total_precio= 0
    total_cantidad = 0
    for x in carrito:
        total_precio += x.total
        total_cantidad += x.cantidad

    compra.Total_a_pagar = total_precio
    compra.id_Usuario = usuario
    compra.cantidad_total = total_cantidad

    compra_hecha = compra.save()
    compra_hecha.id 

    for x in carrito:
        detalle_compra =Detalle_compra()
        detalle_compra.cantidad =x.cantidad
        detalle_compra.Total = x.total
        detalle_compra.id_Producto = x.idProducto
        detalle_compra.id_Compra = compra_hecha
        detalle_compra.save()
        x.delete()

    return HttpResponseRedirect (reverse('principalUsuario'))






