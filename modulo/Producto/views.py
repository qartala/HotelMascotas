from django.shortcuts import render,redirect
from modulo.Producto.models import Categoria, Habitacion, Promocion
from django.urls import reverse
from django.http import HttpResponseRedirect
from modulo.Usuario.models import Usuario
import sweetify


# Create your views here. aqui
def principal(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(tipoPerro__icontains=buscar)
    contexto = {
        'productos': productos
    }
    return render(request, 'base/caso.html', context=contexto)

def listar(request):
    productos = Habitacion.objects.all()
    contexto = {
        'productos': productos
    }
    return render(request, 'base/listar.html', context=contexto)





def modificar(request, idHabitacion):
    try:
        productoEncontrado = Habitacion.objects.get(id=idHabitacion)
    except Habitacion.DoesNotExist:
        return HttpResponseRedirect(reverse('listarProducto'))
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        promociones = Promocion.objects.all()
        contexto = {
            'producto': productoEncontrado,
            'categorias': categorias,
            'promociones': promociones
        }
        return render(request, 'base/modificar.html', contexto)
    elif request.method == 'POST':
        productoEncontrado.imagen = request.FILES.get('imagen', productoEncontrado.imagen)
        productoEncontrado.tipoPerro = request.POST.get('tipoPerro', productoEncontrado.tipoPerro)
        productoEncontrado.kilos = request.POST.get('kilos', productoEncontrado.kilos)
        productoEncontrado.servicio = request.POST.get('servicio', productoEncontrado.servicio)
        productoEncontrado.precio = request.POST.get('precio', productoEncontrado.precio)
        productoEncontrado.tiempoText = request.POST.get('tiempoText', productoEncontrado.tiempoText)
        
        categoriaId = request.POST.get('idCategoria')
        promocionId = request.POST.get('idPromocion')
        
        if categoriaId:
            categoriaEncontrada = Categoria.objects.get(id=categoriaId)
            productoEncontrado.id_categoria = categoriaEncontrada
            
        if promocionId:
            promocionEncontrada = Promocion.objects.get(id=promocionId)
            productoEncontrado.id_Promocion = promocionEncontrada
        
        productoEncontrado.save()
        return HttpResponseRedirect(reverse('listarProducto'))


    

# aqui  
def promociones(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(tipoPerro__icontains=buscar)
    usuario = Usuario.objects.get(idUsuario=request.user.id)
    contexto = {
        'productos': productos,
        'usuario': usuario
    }
    return render(request, 'base/Promociones.html', context=contexto)

def agregarProductos(request):
    categorias = Categoria.objects.all()
    promociones = Promocion.objects.all()
    if request.method =='GET':
        contexto={
            'categorias':categorias,
            'promociones':promociones
        }
        return render(request,'base/AgregarProductos.html',context = contexto)

    elif request.method =='POST':
        nuevoProducto = Habitacion()
        nuevoProducto.imagen = request.FILES.get('imagen')
        nuevoProducto.tipoPerro = request.POST['tipoPerro']
        nuevoProducto.kilos = request.POST['kilos']
        nuevoProducto.servicio = request.POST['servicio']
        nuevoProducto.precio=request.POST['precio']
        nuevoProducto.tiempoText = request.POST['tiempoText']
        categoriaFK = Categoria.objects.get(id = request.POST['idCategoria'])
        promoFK = Promocion.objects.get(id = request.POST['idPromocion'])
        nuevoProducto.id_categoria= categoriaFK
        nuevoProducto.id_Promocion =  promoFK
        try:
            nuevoProducto.save()
        except Exception as ex:
            codigo_error =int (ex.args[0])
            if codigo_error == 1264:
                contexto = {
                    'tipoPerro':request.POST['tipoPerro'],
                    'idCategoria':int(request.POST['idCategoria']),
                    'idPromocion':int(request.POST['idPromocion']),
                
                    'categorias':categorias,
                    'promociones':promociones
                }
                sweetify.warning(request, 'El precio no cumple con el formato debido')  
                return render(request,'base/AgregarProductos.html',context = contexto)
        sweetify.success(request, 'Producto agregado con éxito!!!')    
        return HttpResponseRedirect(reverse('agregarProductos'))

def agregarCategoria(request):
    if request.method == 'GET':
        return render(request,'base/AgregarCategoria.html')

    elif request.method =='POST':
        nuevaCategoria = Categoria()
        nuevaCategoria.nombre = request.POST['nombre']
        nuevaCategoria.save()
        sweetify.success(request, 'Categoria creada con éxito!!!')
        return HttpResponseRedirect(reverse('agregarCategoria'))
        

def crearOferta(request):
    if request.method == 'GET':
        return render(request,'base/crear_oferta.html')

    elif request.method =='POST':
        nuevaPromo = Promocion()
        nuevaPromo.porc_descuento = request.POST['porcentaje']
        nuevaPromo.f_inicio = request.POST['f_inicio']
        nuevaPromo.f_termino = request.POST['f_termino']
        nuevaPromo.nombre = request.POST['nombre']
        
            
        try:
            nuevaPromo.save()
        except Exception as ex:
            codigo_error =int(ex.args[0])
            if codigo_error == 1264:
                contexto = {
                    'porcentaje':request.POST['porcentaje'],
                    'f_inicio':request.POST['f_inicio'],
                    'f_termino':request.POST['f_termino'],
                    'nombre':request.POST['nombre'],
                    
                }
                sweetify.warning(request, 'El porcentaje debe ser igual o mayor a cero')  
                return render(request,'base/crear_oferta.html',contexto)
    sweetify.success(request, 'Oferta creada con éxito!!!')
    return HttpResponseRedirect(reverse('crearOferta'))

def eliminar(request, idProducto):
    try:
        productoEncontrado = Habitacion.objects.get(id=idProducto)
    except Habitacion.DoesNotExist:
        return HttpResponseRedirect(reverse('listarProducto'))

    if request.method == 'GET':
        contexto = {
            'producto': productoEncontrado
        }
        return render(request, 'base/eliminarProducto.html', contexto)

    elif request.method == 'POST':
        productoEncontrado.delete()
        sweetify.success(request, 'Producto Eliminado con éxito!!!')
        return HttpResponseRedirect(reverse('listarProducto'))


    
