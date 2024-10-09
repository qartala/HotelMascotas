from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from modulo.Usuario.models import Usuario
from .models import Habitacion, Reserva
from .forms import ReservaForm
from django.http import JsonResponse
from datetime import timedelta
import sweetify


# Create your views here. aqui
def principal(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(numero_habitacion__icontains=buscar)
    contexto = {
        'productos': productos
    }
    return render(request, 'base/caso.html', context=contexto)

def admin(request):
        return render(request,'base/admin/inicio.html')

def listar(request):
    productos = Habitacion.objects.all()
    contexto = {
        'productos': productos
    }
    return render(request, 'base/admin/listar.html', context=contexto)





def modificar(request, idHabitacion):
    try:
        productoEncontrado = Habitacion.objects.get(id=idHabitacion)
    except Habitacion.DoesNotExist:
        return HttpResponseRedirect(reverse('listarProducto'))
    if request.method == 'GET':
        # categorias = Categoria.objects.all()
        # promociones = Promocion.objects.all()
        contexto = {
            'producto': productoEncontrado,
            # 'categorias': categorias,
            # 'promociones': promociones
        }
        return render(request, 'base/admin/modificar.html', contexto)
    elif request.method == 'POST':
        productoEncontrado.imagen_habitacion = request.FILES.get('imagen_habitacion', productoEncontrado.imagen_habitacion)
        productoEncontrado.numero_habitacion = request.POST.get('numero_habitacion', productoEncontrado.numero_habitacion)
        productoEncontrado.tipo_habitacion = request.POST.get('tipo_habitacion', productoEncontrado.tipo_habitacion)
        # productoEncontrado.servicio = request.POST.get('servicio', productoEncontrado.servicio)
        productoEncontrado.precio = request.POST.get('precio', productoEncontrado.precio)
        # productoEncontrado.tiempoText = request.POST.get('tiempoText', productoEncontrado.tiempoText)
        
        # categoriaId = request.POST.get('idCategoria')
        # promocionId = request.POST.get('idPromocion')
        
        # if categoriaId:
        #     categoriaEncontrada = Categoria.objects.get(id=categoriaId)
        #     productoEncontrado.id_categoria = categoriaEncontrada
            
        # if promocionId:
        #     promocionEncontrada = Promocion.objects.get(id=promocionId)
        #     productoEncontrado.id_Promocion = promocionEncontrada
        
        productoEncontrado.save()
        return HttpResponseRedirect(reverse('listarProducto'))


    

# aqui  
# def promociones(request):
#     buscar = request.GET.get("buscar", "")
#     productos = Habitacion.objects.filter(tipoPerro__icontains=buscar)
#     usuario = Usuario.objects.get(idUsuario=request.user.id)
#     contexto = {
#         'productos': productos,
#         'usuario': usuario
#     }
#     return render(request, 'base/Promociones.html', context=contexto)

def agregarProductos(request):
    # categorias = Categoria.objects.all()
    # promociones = Promocion.objects.all()
    if request.method =='GET':
        contexto={
            # 'categorias':categorias,
            # 'promociones':promociones
        }
        return render(request,'base/admin/AgregarProductos.html',context = contexto)

    elif request.method =='POST':
        nuevoProducto = Habitacion()
        nuevoProducto.imagen_habitacion = request.FILES.get('imagen_habitacion')
        nuevoProducto.numero_habitacion = request.POST['numero_habitacion']
        nuevoProducto.tipo_habitacion = request.POST['tipo_habitacion']
        # nuevoProducto.servicio = request.POST['servicio']
        nuevoProducto.precio=request.POST['precio']
        # categoriaFK = Categoria.objects.get(id = request.POST['idCategoria'])
        # promoFK = Promocion.objects.get(id = request.POST['idPromocion'])
        # nuevoProducto.id_categoria= categoriaFK
        # nuevoProducto.id_Promocion =  promoFK
        try:
            nuevoProducto.save()
        except Exception as ex:
            codigo_error =int (ex.args[0])
            if codigo_error == 1062:
                print(ex)
                contexto = {
                    'numero_habitacion':request.POST['numero_habitacion'],
                    # 'idCategoria':int(request.POST['idCategoria']),
                    # 'idPromocion':int(request.POST['idPromocion']),
                    # 'categorias':categorias,
                    # 'promociones':promociones
                }
                sweetify.warning(request, 'El numero de habitacion esta en uso')
                return render(request,'base/admin/AgregarProductos.html',context = contexto)
        sweetify.success(request, 'Producto agregado con éxito!!!')    
        return HttpResponseRedirect(reverse('agregarProductos'))

# def agregarCategoria(request):
#     if request.method == 'GET':
#         return render(request,'base/AgregarCategoria.html')

    # elif request.method =='POST':
        # nuevaCategoria = Categoria()
        # nuevaCategoria.nombre = request.POST['nombre']
        # nuevaCategoria.save()
        # sweetify.success(request, 'Categoria creada con éxito!!!')
    #     return HttpResponseRedirect(reverse('agregarCategoria'))
        

# def crearOferta(request):
#     if request.method == 'GET':
#         return render(request,'base/crear_oferta.html')

#     elif request.method =='POST':
#         nuevaPromo = Promocion()
#         nuevaPromo.porc_descuento = request.POST['porcentaje']
#         nuevaPromo.f_inicio = request.POST['f_inicio']
#         nuevaPromo.f_termino = request.POST['f_termino']
#         nuevaPromo.nombre = request.POST['nombre']
        
            
#         try:
#             nuevaPromo.save()
#         except Exception as ex:
#             codigo_error =int(ex.args[0])
#             if codigo_error == 1264:
#                 contexto = {
#                     'porcentaje':request.POST['porcentaje'],
#                     'f_inicio':request.POST['f_inicio'],
#                     'f_termino':request.POST['f_termino'],
#                     'nombre':request.POST['nombre'],
                    
#                 }
#                 sweetify.warning(request, 'El porcentaje debe ser igual o mayor a cero')  
#                 return render(request,'base/crear_oferta.html',contexto)
#     sweetify.success(request, 'Oferta creada con éxito!!!')
#     return HttpResponseRedirect(reverse('crearOferta'))

def eliminar(request, idProducto):
    try:
        productoEncontrado = Habitacion.objects.get(id=idProducto)
    except Habitacion.DoesNotExist:
        return HttpResponseRedirect(reverse('listarProducto'))

    if request.method == 'GET':
        contexto = {
            'producto': productoEncontrado
        }
        return render(request, 'base/admin/eliminarProducto.html', contexto)

    elif request.method == 'POST':
        productoEncontrado.delete()
        sweetify.success(request, 'Producto Eliminado con éxito!!!')
        return HttpResponseRedirect(reverse('listarProducto'))


    
def reservar_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id=habitacion_id)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']

            # Verificar si la habitación está disponible
            if Reserva.verificar_disponibilidad(habitacion, fecha_inicio, fecha_fin):
                nueva_reserva = form.save(commit=False)
                nueva_reserva.habitacion = habitacion
                nueva_reserva.cliente = request.user  # Asigna el cliente actual
                nueva_reserva.precio_total = nueva_reserva.calcular_precio_total()
                nueva_reserva.save()
                sweetify.success(request, 'Reserva realizada con éxito')
                return redirect('principalUsuario')  # Redirigir a una página de confirmación
            else:
                sweetify.error(request, 'La habitación no está disponible en las fechas seleccionadas.')
        else:
            # Mostrar errores de formulario
            sweetify.error(request, 'Error en el formulario: ' + str(form.errors))
    else:
        form = ReservaForm()

    return redirect('principalUsuario')



def obtener_reservas_json(request):
    reservas = Reserva.objects.all()
    eventos = []

    for reserva in reservas:
        eventos.append({
            'title': f'Habitación {reserva.habitacion.numero_habitacion}',
            'start': reserva.fecha_inicio.strftime('%Y-%m-%d'),
            'end': (reserva.fecha_fin + timedelta(days=1)).strftime('%Y-%m-%d'),  # FullCalendar excluye la fecha final
            'backgroundColor': 'red'  # Puedes cambiar el color para indicar que está reservada
        })

    return JsonResponse(eventos, safe=False)  # Se envía JSON

def reservas_hotel(request):
        return render(request,'base/reservas_hotel.html')