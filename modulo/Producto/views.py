from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Habitacion, Reserva
from .forms import ReservaForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta
from django.core.mail import send_mail
from modulo.Producto.models import Membresia
from modulo.Colaborador.models import Colaborador
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


    



def agregarProductos(request):
    if request.method =='GET':
        contexto={
        }
        return render(request,'base/admin/AgregarProductos.html',context = contexto)

    elif request.method =='POST':
        nuevoProducto = Habitacion()
        nuevoProducto.imagen_habitacion = request.FILES.get('imagen_habitacion')
        nuevoProducto.numero_habitacion = request.POST['numero_habitacion']
        nuevoProducto.tipo_habitacion = request.POST['tipo_habitacion']
        nuevoProducto.precio=request.POST['precio']
        try:
            nuevoProducto.save()
        except Exception as ex:
            codigo_error =int (ex.args[0])
            if codigo_error == 1062:
                print(ex)
                contexto = {
                    'numero_habitacion':request.POST['numero_habitacion'],
                }
                sweetify.warning(request, 'El numero de habitacion esta en uso')
                return render(request,'base/admin/AgregarProductos.html',context = contexto)
        sweetify.success(request, 'Producto agregado con éxito!!!')    
        return HttpResponseRedirect(reverse('agregarProductos'))

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



def crear_membresia(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descuento = request.POST['descuento']
        duracion = request.POST['duracion_dias']
        valor = request.POST['valor']  # Captura el valor de la membresía desde el formulario

        # Crear y guardar la membresía con el nuevo campo valor
        nueva_membresia = Membresia(
            nombre=nombre, 
            descuento=descuento,
            duracion_dias=duracion, 
            valor=valor  # Guarda el valor
        )
        nueva_membresia.save()

        sweetify.success(request, 'Membresía creada exitosamente.')
        return redirect('crear_membresia')

    return render(request, 'base/admin/crearMembresia.html')

def gestionar_membresias(request):
    membresias = Membresia.objects.all()  # Obtener todas las membresías

    if request.method == 'POST':
        membresia_id = request.POST.get('membresia_id')
        accion = request.POST.get('accion')

    return render(request, 'base/admin/gestionMembresia.html', {'membresias': membresias})

def editar_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    print("Descuento:", membresia.descuento)
    print("Valor:", membresia.valor)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descuento = request.POST.get('descuento')
        duracion_dias = request.POST.get('duracion_dias')
        valor = request.POST.get('valor')

        membresia.nombre = nombre
        membresia.descuento = descuento
        membresia.duracion_dias = duracion_dias
        membresia.valor = valor
        membresia.save()

        sweetify.success(request, 'Membresía actualizada con éxito.')
        return redirect('gestionar_membresias')

    return render(request, 'base/admin/editarMembresia.html', {'membresia': membresia})

def eliminar_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    membresia.delete()
    sweetify.success(request, 'Membresía eliminada con éxito.')
    return redirect('gestionar_membresias')

def solicitudes_admin(request):
    storage = messages.get_messages(request)
    for message in storage:
        if "Inicio de sesión exitoso" in message.message:
            message.used = True  

    solicitudes = Colaborador.objects.filter(estado='pendiente')
    
    return render(request, 'base/admin/solicitudes.html', {'solicitudes': solicitudes})

def gestionar_solicitud(request, colaborador_id, accion):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    if accion == 'aprobar':
        colaborador.estado = 'aprobado'
        colaborador.save()
        send_mail(
            'Solicitud Aprobada',
            '¡Felicidades! Tu solicitud ha sido aprobada.',
            'petsteamcl@gmail.com',
            [colaborador.email],
            fail_silently=False,
        )

        messages.success(request, 'Colaborador aprobado con éxito.')
    elif accion == 'rechazar':
        colaborador.delete()
        send_mail(
            'Solicitud Rechazada',
            'Lo sentimos, tu solicitud ha sido rechazada.',
            'petsteamcl@gmail.com',
            [colaborador.email],
            fail_silently=False,
        )

        messages.error(request, 'Colaborador rechazado y eliminado.')

    return redirect('solicitudes_admin')