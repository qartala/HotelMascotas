from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger,EmptyPage
from django.http import HttpResponseRedirect
from .models import Habitacion, Reserva
from .forms import ReservaForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta
from django.core.mail import send_mail
from modulo.Producto.models import Membresia
from modulo.Colaborador.models import Colaborador
from modulo.Usuario.models import Usuario
import random
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
    paginator = Paginator(productos, 5)  # Mostrar 5 habitaciones por página
    
    # Validar la página que se intenta acceder
    page_number = request.GET.get('page', 1)

    try:
        # Asegurarnos de que page_number sea un entero mayor que 0
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        # Obtener la página solicitada
        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        # Si ocurre un error, redirige a la primera página
        return redirect('?page=1')
    except EmptyPage:
        # Si la página está fuera de rango, redirige a la última página
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/listar.html', context=contexto)

def modificar(request, idHabitacion):
    habitacion = get_object_or_404(Habitacion, id=idHabitacion)
    
    if request.method == 'GET':
        contexto = {
            'habitacion': habitacion,
        }
        return render(request, 'base/admin/modificar.html', contexto)

    elif request.method == 'POST':
        # Obtener el nuevo número de habitación del formulario
        nuevo_numero = request.POST.get('numero_habitacion', habitacion.numero_habitacion)

        # Verificar si el nuevo número ya existe en otra habitación
        if Habitacion.objects.filter(numero_habitacion=nuevo_numero).exclude(id=idHabitacion).exists():
            sweetify.error(request, 'Este número de habitación ya existe. Por favor, elige otro.')
            return HttpResponseRedirect(reverse('listarProducto'))

        # Actualizar los campos de la habitación
        habitacion.imagen_habitacion = request.FILES.get('imagen_habitacion', habitacion.imagen_habitacion)
        habitacion.numero_habitacion = nuevo_numero
        habitacion.tipo_habitacion = request.POST.get('tipo_habitacion', habitacion.tipo_habitacion)
        habitacion.precio = request.POST.get('precio', habitacion.precio)
        
        # Guardar los cambios
        habitacion.save()

        sweetify.success(request, 'La habitación se modificó correctamente.')
        return HttpResponseRedirect(reverse('listarProducto'))



def agregarProductos(request):
    if request.method =='GET':
        contexto={
        }
        return render(request,'base/admin/AgregarProductos.html',context = contexto)

    elif request.method == 'POST':
        numero_habitacion = request.POST.get('numero_habitacion')
        tipo_habitacion = request.POST.get('tipo_habitacion')
        precio = request.POST.get('precio')
        imagen_habitacion = request.FILES.get('imagen_habitacion')

        # Verificar si ya existe una habitación con ese número
        if Habitacion.objects.filter(numero_habitacion=numero_habitacion).exists():
            sweetify.error(request, 'El número de habitación ya existe. Por favor, elige otro.')
            return redirect('listarProducto')

        # Crear la nueva habitación
        Habitacion.objects.create(
            numero_habitacion=numero_habitacion,
            tipo_habitacion=tipo_habitacion,
            precio=precio,
            imagen_habitacion=imagen_habitacion
        )
        sweetify.success(request, 'Habitación creada exitosamente.')
        return redirect('listarProducto')

def eliminar(request, idProducto):
    try:
        productoEncontrado = Habitacion.objects.get(id=idProducto)
        productoEncontrado.delete()
        sweetify.success(request, 'La habitacion y sus reservas asociadas se eliminaron con éxito!')
        return HttpResponseRedirect(reverse('listarProducto'))
    except Habitacion.DoesNotExist:
        sweetify.error(request, 'Error al eliminar la habitacion')
        return HttpResponseRedirect(reverse('listarProducto'))


    
def reservar_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id=habitacion_id)
    
    # Obtener el usuario y su perfil
    perfil_usuario = Usuario.objects.get(idUsuario=request.user)
    
    # Obtener la membresía del usuario, si tiene una
    membresia = perfil_usuario.membresia
    
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
                
                # Calcular el precio total original
                precio_original = nueva_reserva.calcular_precio_total()
                
                # Aplicar descuento si el usuario tiene una membresía
                if membresia:
                    descuento = float(membresia.descuento) / 100  # Convertir porcentaje a decimal
                    precio_con_descuento = precio_original * (1 - descuento)
                    nueva_reserva.precio_total = round(precio_con_descuento, 2)  # Redondear a 2 decimales
                else:
                    nueva_reserva.precio_total = precio_original  # Sin descuento

                nueva_reserva.save()
                sweetify.success(request, 'Reserva realizada con éxito')
                return redirect('principalUsuario')  # Redirigir a una página de confirmación
            else:
                sweetify.error(request, 'La habitación no está disponible en las fechas seleccionadas.')
        else:
            # Mostrar errores de formulario
            sweetify.error(request, 'Debes ingresar una mascota para realizar reservas')
    else:
        form = ReservaForm()

    return redirect('principalUsuario')



def obtener_reservas_json(request, habitacion_id):
    habitacion = Habitacion.objects.get(id=habitacion_id)
    
    # Obtener solo las reservas que no están canceladas
    reservas = Reserva.objects.filter(habitacion=habitacion, cancelada=False)
    eventos = []

    def generar_color_aleatorio():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    for reserva in reservas:
        eventos.append({
            'title': f'Habitación {reserva.habitacion.numero_habitacion}',
            'start': reserva.fecha_inicio.strftime('%Y-%m-%d'),
            'end': (reserva.fecha_fin + timedelta(days=1)).strftime('%Y-%m-%d'),  # FullCalendar excluye la fecha final
            'backgroundColor': generar_color_aleatorio()  # Puedes cambiar el color para indicar que está reservada
        })

    return JsonResponse(eventos, safe=False)  # Se envía JSON



def crear_membresia(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descuento = request.POST.get('descuento')
        duracion = request.POST.get('duracion_dias')
        valor = request.POST.get('valor')  # Asegúrate de capturar el campo 'valor'

        if valor:  # Asegúrate de que el valor no sea nulo o vacío
            valor = float(valor)

        # Crear y guardar la membresía
        nueva_membresia = Membresia(nombre=nombre, descuento=descuento, duracion_dias=duracion, valor=valor)
        nueva_membresia.save()

        sweetify.success(request, 'Membresía creada exitosamente.')
        return redirect('gestionar_membresias')

def gestionar_membresias(request):
    membresias = Membresia.objects.all()  # Obtener todas las membresías
    paginator = Paginator(membresias, 5)  # Mostrar 5 membresías por página
    
    # Validar la página que se intenta acceder
    page_number = request.GET.get('page', 1)

    try:
        # Asegurarse de que page_number sea un entero válido y mayor que 0
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        # Obtener la página solicitada
        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        # Si ocurre un error, redirige a la primera página
        return redirect('?page=1')
    except EmptyPage:
        # Si la página está fuera de rango, redirige a la última página
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/gestionMembresia.html', context=contexto)

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

def eliminar_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    membresia.delete()
    sweetify.success(request, 'Membresía eliminada con éxito.')
    return redirect('gestionar_membresias')

def solicitudes_admin(request):
    solicitudes = Colaborador.objects.filter(estado='pendiente')
    paginator = Paginator(solicitudes, 5)  # Mostrar 5 solicitudes por página

    # Validar la página solicitada
    page_number = request.GET.get('page', 1)

    try:
        # Asegúrate de que el número de página sea un entero positivo
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        # Obtener la página solicitada
        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        # Redirige a la primera página si hay un error
        return redirect('?page=1')
    except EmptyPage:
        # Redirige a la última página disponible si la página está fuera de rango
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/solicitudes.html', context=contexto)

def gestionar_solicitud(request, colaborador_id, accion):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    print(colaborador)
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

        sweetify.success(request, 'Colaborador aprobado con éxito.')
        return redirect('solicitudes_admin')

    elif accion == 'rechazar':
        colaborador.delete()
        send_mail(
            'Solicitud Rechazada',
            'Lo sentimos, tu solicitud ha sido rechazada.',
            'petsteamcl@gmail.com',
            [colaborador.email],
            fail_silently=False,
        )

        sweetify.error(request, 'Colaborador rechazado y eliminado.')
        return redirect('solicitudes_admin')

def listar_colaboradores_aprobados(request):
    colaboradores_aprobados = Colaborador.objects.filter(estado='aprobado')
    paginator = Paginator(colaboradores_aprobados, 5)  # Mostrar 5 colaboradores por página

    # Validar la página solicitada
    page_number = request.GET.get('page', 1)

    try:
        # Asegúrate de que el número de página sea un entero positivo
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        # Obtener la página solicitada
        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        # Redirige a la primera página si hay un error
        return redirect('?page=1')
    except EmptyPage:
        # Redirige a la última página disponible si la página está fuera de rango
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/colaboradores_aprobados.html', context=contexto)


from django.utils.timezone import now
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from modulo.Producto.models import Reserva
from modulo.Colaborador.models import Colaborador
import json

def dashboard_admin(request):
    año_actual = now().year

    # Ingresos totales por mes solo para reservas pagadas
    ingresos_mensuales = (
        Reserva.objects.filter(pagado=True, fecha_inicio__year=año_actual)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Sum('precio_total'))
        .order_by('mes')
    )

    # Datos para las habitaciones y sus reservas (solo pagadas)
    reservas_por_habitacion = (
        Reserva.objects.filter(pagado=True)
        .values('habitacion__tipo_habitacion')
        .annotate(total_reservas=Count('id'))
        .order_by('-total_reservas')
    )

    # Preparar datos para los gráficos
    habitaciones = [reserva['habitacion__tipo_habitacion'] for reserva in reservas_por_habitacion]
    total_reservas_habitaciones = [reserva['total_reservas'] for reserva in reservas_por_habitacion]

    # Preparar ingresos totales mensuales
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    ingresos_totales_mensuales = [0] * 12  # Inicializar con 0 para cada mes

    for ingreso in ingresos_mensuales:
        mes_index = ingreso['mes'].month - 1  # Obtener el índice del mes (0-11)
        ingresos_totales_mensuales[mes_index] = ingreso['total']

    # Otros KPIs solo considerando reservas pagadas
    total_reservas_pagadas = Reserva.objects.filter(pagado=True).count()  # Contar solo las reservas pagadas
    total_reservas = Reserva.objects.count()  # Total de todas las reservas
    colaboradores_activos = Colaborador.objects.filter(estado='aprobado').count()  # Contar solo aprobados
    print(f'Total Reservas Pagadas: {total_reservas_pagadas}')
    print(f'Total Reservas: {total_reservas}')

    # Contar las reservas que han sido canceladas
    canceladas = Reserva.objects.filter(cancelada=True).count()  # Contar todas las canceladas
    print(f'Total Reservas canceladas: {canceladas}')
    
    # Calcular la tasa de cancelación
    if total_reservas > 0:
        tasa_cancelacion = round((canceladas / total_reservas * 100), 1)  # Redondear a un decimal
    else:
        tasa_cancelacion = 0  # No hay reservas pagadas, tasa de cancelación es 0

    # Preparar los datos para el template
    dashboard_data = json.dumps({
        'total_reservas_pagadas': total_reservas_pagadas,
        'total_reservas': total_reservas,  # Añadido para mostrar el total general
        'ingresos_totales_mensuales': ingresos_totales_mensuales,
        'meses': meses,
        'colaboradores_activos': colaboradores_activos,
        'tasa_cancelacion': tasa_cancelacion,
        'habitacion_tipos': habitaciones,
        'habitacion_reservas': total_reservas_habitaciones
    })

    return render(request, 'base/admin/dashboard.html', {
        'dashboard_data': dashboard_data
    })