from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger,EmptyPage
from django.http import HttpResponseRedirect
from .models import Habitacion, Reserva
from django.db import models
from django.db.models import Count, Q
from .forms import ReservaForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta
from django.core.mail import send_mail
from modulo.Producto.models import Membresia
from modulo.Colaborador.models import Colaborador
from modulo.Usuario.models import Calificacion, Ficha, Mensaje, Usuario, ReservaServicio
import random
import sweetify
from datetime import date
from .models import Regalia
from django.utils.timezone import now, localtime
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from modulo.Producto.models import Reserva
from modulo.Colaborador.models import Colaborador
import json
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Q

from django.utils.timezone import now
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from django.db.models import Count

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth



from collections import defaultdict

def reservas_activas(request):
    # Obtener las reservas activas
    reservas = Reserva.objects.filter(pagado=True, cancelada=False)

    # Obtener los mensajes no respondidos del administrador
    mensajes_no_respondidos = Mensaje.objects.filter(receptor=request.user, respondido=False)

    # Contar los mensajes no respondidos (sólo aquellos que no han sido respondidos)
    total_mensajes_no_respondidos = mensajes_no_respondidos.count()

    # Asociar mensajes con reservas
    mensajes_por_reserva = defaultdict(list)
    for mensaje in mensajes_no_respondidos:
        mensajes_por_reserva[mensaje.reserva_id].append(mensaje)

    # Actualizar los mensajes que ya fueron respondidos por el admin
    if request.method == 'POST' and 'reserva_id' in request.POST:
        reserva_id = request.POST['reserva_id']
        # Cambiar a respondido los mensajes de la reserva
        mensajes = Mensaje.objects.filter(reserva_id=reserva_id, leido=True, respondido=False)
        if mensajes.exists():
            mensajes.update(respondido=True)  # Marcar como respondidos los mensajes
            total_mensajes_no_respondidos -= mensajes.count()  # Restar los mensajes respondidos del total

    return render(request, 'base/admin/reservas_activas.html', {
        'reservas': reservas,
        'total_mensajes_no_respondidos': total_mensajes_no_respondidos,
        'mensajes_no_respondidos': mensajes_no_respondidos,  # Pasar los mensajes no respondidos
        'mensajes_por_reserva': dict(mensajes_por_reserva),  # Asociación de mensajes con reservas
    })



@require_POST
def iniciar_pago(request, membresia_id, tipo):
    try:
        return HttpResponseRedirect(f"Pago iniciado para la membresía con ID {membresia_id} y tipo {tipo}.")
    except Exception as e:
        return HttpResponseRedirect(f"Ocurrió un error: {str(e)}", status=400)

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
    paginator = Paginator(productos, 5)  

    page_number = request.GET.get('page', 1)

    try:
      
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        return redirect('?page=1')
    except EmptyPage:
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
        nuevo_numero = request.POST.get('numero_habitacion', habitacion.numero_habitacion)

        if Habitacion.objects.filter(numero_habitacion=nuevo_numero).exclude(id=idHabitacion).exists():
            sweetify.error(request, 'Este número de habitación ya existe. Por favor, elige otro.')
            return HttpResponseRedirect(reverse('listarProducto'))

        habitacion.imagen_habitacion = request.FILES.get('imagen_habitacion', habitacion.imagen_habitacion)
        habitacion.numero_habitacion = nuevo_numero
        habitacion.tipo_habitacion = request.POST.get('tipo_habitacion', habitacion.tipo_habitacion)
        habitacion.precio = request.POST.get('precio', habitacion.precio)
        
        habitacion.save()

        sweetify.success(request, 'La habitación se modificó correctamente.')
        return HttpResponseRedirect(reverse('listarProducto'))



def agregarProductos(request):

    if request.method == 'POST':
        numero_habitacion = request.POST.get('numero_habitacion')
        tipo_habitacion = request.POST.get('tipo_habitacion')
        precio = request.POST.get('precio')
        imagen_habitacion = request.FILES.get('imagen_habitacion')

        if Habitacion.objects.filter(numero_habitacion=numero_habitacion).exists():
            sweetify.error(request, 'El número de habitación ya existe. Por favor, elige otro.')
            return redirect('listarProducto')

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


from modulo.Producto.models import Reserva
def reservar_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id=habitacion_id)
    
    perfil_usuario = Usuario.objects.get(idUsuario=request.user)
    
    membresia = perfil_usuario.membresia
    
    if membresia and perfil_usuario.fecha_inicio_membresia:
        hoy = date.today()
        fecha_vencimiento = perfil_usuario.fecha_inicio_membresia + timedelta(days=membresia.duracion_dias)
        if hoy > fecha_vencimiento:
                perfil_usuario.membresia = None
                perfil_usuario.fecha_inicio_membresia = None
                perfil_usuario.save()  
                membresia = None
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            
            # Verificar si la habitación está disponible
            if Reserva.verificar_disponibilidad(habitacion, fecha_inicio, fecha_fin):
                nueva_reserva = form.save(commit=False)
                nueva_reserva.habitacion = habitacion
                nueva_reserva.cliente = request.user 

                precio_original = nueva_reserva.calcular_precio_total()
                
                # Aplicar descuento si el usuario tiene una membresía
                if membresia:
                    descuento = float(membresia.descuento) / 100  
                    precio_con_descuento = precio_original * (1 - descuento)
                    nueva_reserva.precio_total = round(precio_con_descuento, 2)  
                else:
                    nueva_reserva.precio_total = precio_original  
                nueva_reserva.save()
                sweetify.success(request, 'Reserva realizada con éxito')
                return redirect('principalUsuario')  
            nueva_reserva = form.save(commit=False)
            nueva_reserva.habitacion = habitacion
            nueva_reserva.cliente = request.user
            precio_original = nueva_reserva.calcular_precio_total()
            if membresia:
                descuento = float(membresia.descuento) / 100
                nueva_reserva.precio_total = round(precio_original * (1 - descuento), 2)
            else:
                sweetify.error(request, 'La habitación no está disponible en las fechas seleccionadas.')
        else:
            sweetify.error(request, 'Debes ingresar una mascota para realizar reservas')
            nueva_reserva.precio_total = precio_original
            nueva_reserva.save()
            sweetify.success(request, 'Reserva realizada con éxito.')
            return redirect('principalUsuario')
    else:
        form = ReservaForm()

    return redirect('principalUsuario')


def obtener_reservas_json(request, habitacion_id):
    habitacion = Habitacion.objects.get(id=habitacion_id)
    
    reservas = Reserva.objects.filter(habitacion=habitacion, cancelada=False, checkout=False)  # Excluir reservas con checkout
    eventos = []

    def generar_color_aleatorio():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    for reserva in reservas:
        eventos.append({
            'title': f'Habitación {reserva.habitacion.numero_habitacion}',
            'start': reserva.fecha_inicio.strftime('%Y-%m-%d'),
            'end': (reserva.fecha_fin + timedelta(days=1)).strftime('%Y-%m-%d'),  
            'backgroundColor': generar_color_aleatorio()  
        })

    return JsonResponse(eventos, safe=False)



def crear_membresia(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descuento = request.POST.get('descuento')
        duracion = request.POST.get('duracion_dias')
        valor = request.POST.get('valor')  
        if valor:  
            valor = float(valor)


        nueva_membresia = Membresia(nombre=nombre, descuento=descuento, duracion_dias=duracion, valor=valor)
        nueva_membresia.save()

        sweetify.success(request, 'Membresía creada exitosamente.')
        return redirect('gestionar_membresias')

def gestionar_membresias(request):
    membresias = Membresia.objects.all()  
    paginator = Paginator(membresias, 5)  
    
    page_number = request.GET.get('page', 1)

    try:
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        return redirect('?page=1')
    except EmptyPage:
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
    paginator = Paginator(solicitudes, 5)  

    page_number = request.GET.get('page', 1)

    try:
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
      
        return redirect('?page=1')
    except EmptyPage:
        
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/solicitudes.html', context=contexto)

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
        sweetify.success(request, 'Colaborador aprobado con éxito.')
        return redirect('solicitudes_admin')

    elif accion == 'rechazar':
        comentario_rechazo = request.POST.get('comentario_rechazo')
        
        if not comentario_rechazo:
            sweetify.error(request, 'Debes proporcionar un motivo para el rechazo.')
            return redirect('solicitudes_admin')

        # Puedes guardar el comentario en un campo adicional o enviarlo en el correo
        send_mail(
            'Solicitud Rechazada',
            f'Lo sentimos, tu solicitud ha sido rechazada. Motivo: {comentario_rechazo}',
            'petsteamcl@gmail.com',
            [colaborador.email],
            fail_silently=False,
        )
        
        colaborador.delete()
        sweetify.success(request, 'Colaborador rechazado y eliminado.')
        return redirect('solicitudes_admin')

def listar_colaboradores_aprobados(request):
    colaboradores_aprobados = Colaborador.objects.filter(estado='aprobado')
    paginator = Paginator(colaboradores_aprobados, 5)  

    page_number = request.GET.get('page', 1)

    try:
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")


        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):

        return redirect('?page=1')
    except EmptyPage:
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/colaboradores_aprobados.html', context=contexto)









from django.shortcuts import render
from django.utils.timezone import localtime, now
from django.db.models import Sum, Count, Q
from modulo.Producto.models import Reserva, Habitacion, Regalia
from modulo.Usuario.models import Usuario, Ficha, ReservaServicio
from modulo.Colaborador.models import Colaborador


def dashboard_admin(request):

    
    # Contar las calificaciones bajas (menores o iguales a 4)
    calificaciones_bajas = Calificacion.objects.filter(calificacion__lte=4)
    calificaciones_bajas_count = calificaciones_bajas.count()

    # Obtener mensajes no respondidos
    mensajes_no_respondidos = Mensaje.objects.filter(receptor=request.user, respondido=False)
    total_mensajes_no_respondidos = mensajes_no_respondidos.count()



    # Fecha actual
    fecha_actual = now()  # Obtiene la fecha y hora actual
    hoy = localtime(now()).date()
    primer_dia_mes = hoy.replace(day=1)
    # Define qué es una calificación baja (por ejemplo, menor a 3)
    calificaciones_bajas = Calificacion.objects.filter(calificacion__lt=3)
    

    

     # Fecha actual
    hoy = localtime(now()).date()
    primer_dia_mes = hoy.replace(day=1)

    DIAS_SEMANA = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    # Obtener el total de habitaciones
    total_habitaciones = Habitacion.objects.count()

    # Inicializamos ocupación con todos los días a 0
    ocupacion_por_dia = {day: 0 for day in DIAS_SEMANA.values()}

    # Solo procesamos el día actual
    if total_habitaciones > 0:
        dia_semana = DIAS_SEMANA[hoy.strftime("%A")]  # Solo el día actual

        # Contamos las habitaciones ocupadas para el día actual
        habitaciones_ocupadas = Reserva.objects.filter(
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            pagado=True,
            cancelada=False,
            check_in=True,
            checkout=False
        ).values('habitacion').annotate(count=Count('habitacion')).filter(count__gt=0).count()

        # Calculamos el porcentaje de ocupación solo para el día actual
        ocupacion_por_dia[dia_semana] = round((habitaciones_ocupadas / total_habitaciones) * 100, 2)


    # Convierte el diccionario ocupacion_por_dia a JSON
    ocupacion_por_dia_json = json.dumps(ocupacion_por_dia)
    # ========================== Servicios Realizados Hoy ==========================
    servicios_hoy = ReservaServicio.objects.filter(
        fecha_reservada=hoy,
        pagado=True,
        cancelada=False
    )

    # ========================== Check-in y Check-out Pendientes Hoy ==========================
    reservas_check_in = Reserva.objects.filter(
        fecha_inicio=hoy,
        pagado=True,
        cancelada=False,
        check_in=False
    )
    reservas_check_out = Reserva.objects.filter(
        fecha_fin=hoy,
        pagado=True,
        cancelada=False,
        check_in=True,
        checkout=False
    )

    pendientes_check_in_hoy = reservas_check_in.count()
    pendientes_check_out_hoy = reservas_check_out.count()

    # ========================== Check-in y Check-out Acumulados ==========================
    pendientes_check_in_acumulados = Reserva.objects.filter(
        pagado=True,
        cancelada=False,
        check_in=False
    ).count()

    pendientes_check_out_acumulados = Reserva.objects.filter(
        pagado=True,
        cancelada=False,
        check_in=True,
        checkout=False
    ).count()

    # ===================== Datos Generales =====================
    total_reservas = Reserva.objects.count()
    ingresos_totales = Reserva.objects.filter(
        pagado=True,
        cancelada=False
    ).aggregate(total=Sum('precio_total'))['total'] or 0

    clientes = Usuario.objects.filter(trabajador=False).count()
    colaboradores_activos = Colaborador.objects.filter(estado='aprobado').count()

    # ========================== Perros que Llegan y se Van Hoy ==========================
    perros_llegan_hoy = pendientes_check_in_hoy
    perros_se_van_hoy = pendientes_check_out_hoy

    # ========================== Porcentaje de Ocupación ==========================
    total_habitaciones = Habitacion.objects.count()
    habitaciones_ocupadas = Reserva.objects.filter(
        pagado=True,
        cancelada=False,
        check_in=True,
        checkout=False
    ).values('habitacion').distinct().count()

    porcentaje_ocupacion = (
        round((habitaciones_ocupadas / total_habitaciones) * 100, 1)
        if total_habitaciones > 0 else 0
    )

    # ========================== Stock de Regalos ==========================
    regalos_bajo_stock = Regalia.objects.filter(stock__lte=5).count()
    total_regalos = Regalia.objects.aggregate(total_stock=Sum('stock'))['total_stock'] or 0

    # ========================== Mascotas Actualmente Hospedadas ==========================
    mascotas_hospedadas = Reserva.objects.filter(
        pagado=True,
        cancelada=False,
        check_in=True,
        checkout=False
    ).count()

    # ========================== Servicios Realizados Hoy ==========================
    servicios_realizados_hoy = servicios_hoy.count()

    # ========================== Total Servicios Realizados ==========================
    servicios_realizados_totales = ReservaServicio.objects.filter(
        pagado=True,
        cancelada=False
    ).count()

    # Contexto para el template
    dashboard_data = {
        'fecha_actual': fecha_actual,
        'total_reservas': total_reservas,
        'ingresos_totales': ingresos_totales,
        'clientes': clientes,
        'colaboradores_activos': colaboradores_activos,
        'pendientes_check_in_hoy': pendientes_check_in_hoy,  # Conteo para la carta
        'pendientes_check_out_hoy': pendientes_check_out_hoy,  # Conteo para la carta
        'pendientes_check_in_acumulados': pendientes_check_in_acumulados,
        'pendientes_check_out_acumulados': pendientes_check_out_acumulados,
        'perros_llegan_hoy': perros_llegan_hoy,
        'perros_se_van_hoy': perros_se_van_hoy,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'regalos_bajo_stock': regalos_bajo_stock,
        'total_regalos': total_regalos,
        'mascotas_hospedadas': mascotas_hospedadas,
        'servicios_hoy': servicios_realizados_hoy,
        'servicios_totales': servicios_realizados_totales,
        'reservas_check_in': reservas_check_in,  # Queryset para tabla Check-in
        'reservas_check_out': reservas_check_out,  # Queryset para tabla Check-out
        "ocupacion_por_dia": ocupacion_por_dia_json,  # Añade estos datos al contexto
        'calificaciones_bajas': calificaciones_bajas,
        "calificaciones_bajas_count": calificaciones_bajas_count,
        'total_mensajes_no_respondidos': total_mensajes_no_respondidos,  # Añadir al contexto
    }

    print(ocupacion_por_dia)  # Verifica los valores calculados en la consola



    return render(request, 'base/admin/dashboard.html', dashboard_data)


from django.db.models import Avg, Count

def listar_calificaciones_bajas(request):
    # Filtrar calificaciones bajas (por ejemplo, menor o igual a 4)
    calificaciones_bajas = Calificacion.objects.filter(calificacion__lte=4)

    # Obtener métricas adicionales
    total_calificaciones = calificaciones_bajas.count()  # Total de calificaciones bajas (≤ 4)
    promedio_calificaciones = calificaciones_bajas.aggregate(promedio=Avg('calificacion'))['promedio'] or 0  # Promedio general
    total_comentarios = calificaciones_bajas.count()  # Total de comentarios con calificación baja

    # Distribución por calificación (para el gráfico)
    calificaciones_1 = calificaciones_bajas.filter(calificacion=1).count()
    calificaciones_2 = calificaciones_bajas.filter(calificacion=2).count()
    calificaciones_3 = calificaciones_bajas.filter(calificacion=3).count()
    calificaciones_4 = calificaciones_bajas.filter(calificacion=4).count()
    calificaciones_5 = Calificacion.objects.filter(calificacion=5).count()  # Opcional para mantener el gráfico completo

    # Contexto para el template
    context = {
        "calificaciones_bajas": calificaciones_bajas,
        "total_calificaciones": total_calificaciones,
        "promedio_calificaciones": promedio_calificaciones,
        "total_comentarios": total_comentarios,
        "calificaciones_1": calificaciones_1,
        "calificaciones_2": calificaciones_2,
        "calificaciones_3": calificaciones_3,
        "calificaciones_4": calificaciones_4,
        "calificaciones_5": calificaciones_5,  # Solo para completar el gráfico si lo necesitas
    }

    return render(request, "base/admin/calificaciones_bajas.html", context)


def marcar_calificacion_revisada(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)
    calificacion.revisada = True  # Asegúrate de que este campo exista en el modelo
    calificacion.save()
    messages.success(request, "La calificación fue marcada como revisada exitosamente.")
    return redirect("listar_calificaciones_bajas")




def marcar_calificacion_revisada(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)
    calificacion.revisada = True  # Asume que tienes este campo en el modelo
    calificacion.save()
    messages.success(request, 'La calificación ha sido marcada como revisada.')
    return redirect('dashboard_admin')

def responder_calificacion(request, calificacion_id):
    if request.method == "POST":
        respuesta = request.POST.get("respuesta")
        calificacion = get_object_or_404(Calificacion, id=calificacion_id)  # Ajusta tu modelo
        usuario = calificacion.usuario  # Relación con el usuario desde el modelo Calificacion
        correo_usuario = usuario.email  # Accede al correo directamente desde el modelo User

        # Intenta enviar el correo
        try:
            send_mail(
                subject="Respuesta a tu comentario",
                message=(
                    f"Hola {usuario.username},\n\n"
                    f"Gracias por tu comentario. Aquí está nuestra respuesta:\n\n"
                    f"{respuesta}\n\n"
                    "Saludos, equipo Hotel Pets Team."
                ),
                from_email="petsteamcl@gmail.com",  # Cambia esto si necesitas usar un correo diferente
                recipient_list=[correo_usuario],
                fail_silently=False,
            )
            # Mostrar notificación de éxito con Sweetify
            sweetify.success(
                request,
                "Mensaje enviado con éxito",
                text=f"Se ha enviado la respuesta al correo: {correo_usuario}.",
                timer=3000,
                icon="success",
            )
        except Exception as e:
            # Mostrar notificación de error con Sweetify
            sweetify.error(
                request,
                "Error al enviar el mensaje",
                text=f"No se pudo enviar el correo. Detalle: {str(e)}",
                timer=3000,
                icon="error",
            )

        return redirect("dashboard_admin")


def ingresos_grafico(request):
    # Obtén los ingresos agrupados por años
    ingresos_por_anio = (
        Reserva.objects.filter(pagado=True)
        .annotate(anio=models.functions.ExtractYear('fecha_inicio'))
        .values('anio')
        .annotate(total_ingresos=Sum('precio_total'))
        .order_by('anio')
    )

    # Preparar los datos para el gráfico
    anios = [dato['anio'] for dato in ingresos_por_anio]
    ingresos = [dato['total_ingresos'] for dato in ingresos_por_anio]

    context = {
        'anios': anios,
        'ingresos': ingresos,
    }

    return render(request, 'base/admin/ingresos_grafico.html', context)


def marcar_calificacion_revisada(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)
    calificacion.revisada = True  # Asume que tienes este campo en el modelo
    calificacion.save()
    messages.success(request, 'La calificación ha sido marcada como revisada.')
    return redirect('dashboard_admin')


def marcar_calificacion_revisada(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)
    calificacion.revisada = True  # Asegúrate de que este campo exista en el modelo
    calificacion.save()
    messages.success(request, "La calificación fue marcada como revisada exitosamente.")
    return redirect("listar_calificaciones_bajas")




def dashboard_operativo(request):
    hoy = localtime(now()).date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
    fin_semana = inicio_semana + timedelta(days=6)  # Domingo de la semana actual

    # ===================== Cálculo de Ingresos Diarios =====================
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    ingresos_diarios = (
        Reserva.objects.filter(
            pagado=True,
            cancelada=False,
            fecha_inicio__range=[inicio_semana, fin_semana]
        )
        .annotate(dia=TruncDay('fecha_inicio'))
        .values('dia')
        .annotate(total=Sum('precio_total'))
        .order_by('dia')
    )

    ingresos_totales_diarios = [0] * 7
    for ingreso in ingresos_diarios:
        dia_index = ingreso['dia'].weekday()
        ingresos_totales_diarios[dia_index] = ingreso['total']

    # ===================== Cálculo de Ingresos Semanales =====================
    semanas_mes = ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5']
    primer_dia_mes = date(hoy.year, hoy.month, 1)
    primera_semana_mes = primer_dia_mes.isocalendar()[1]

    ingresos_semanales = (
        Reserva.objects.filter(
            pagado=True,
            cancelada=False,
            fecha_inicio__year=hoy.year,
            fecha_inicio__month=hoy.month
        )
        .annotate(semana=TruncWeek('fecha_inicio'))
        .values('semana')
        .annotate(total=Sum('precio_total'))
        .order_by('semana')
    )

    ingresos_totales_semanales = [0] * 5
    for ingreso in ingresos_semanales:
        semana_actual = ingreso['semana'].isocalendar()[1]
        semana_index = semana_actual - primera_semana_mes
        if 0 <= semana_index < 5:
            ingresos_totales_semanales[semana_index] = ingreso['total']

    # ===================== Cálculo de Reservas Diarias =====================
    reservas_diarias = (
        Reserva.objects.filter(
            pagado=True,
            cancelada=False,
            fecha_inicio__range=[inicio_semana, fin_semana]
        )
        .annotate(dia=TruncDay('fecha_inicio'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    reservas_totales_diarias = [0] * 7
    for reserva in reservas_diarias:
        dia_index = reserva['dia'].weekday()
        reservas_totales_diarias[dia_index] = reserva['total']

    total_reservas_hoy = Reserva.objects.filter(fecha_inicio=hoy).count()
    canceladas_hoy = Reserva.objects.filter(fecha_inicio=hoy, cancelada=True).count()
    tasa_cancelacion_diaria = round((canceladas_hoy / total_reservas_hoy * 100), 1) if total_reservas_hoy > 0 else 0

    # ===================== Cálculo de Reservas Semanales =====================
    reservas_semanales = (
        Reserva.objects.filter(
            pagado=True,
            cancelada=False,
            fecha_inicio__year=hoy.year,
            fecha_inicio__month=hoy.month
        )
        .annotate(semana=TruncWeek('fecha_inicio'))
        .values('semana')
        .annotate(total=Count('id'))
        .order_by('semana')
    )

    reservas_totales_semanales = [0] * 5
    for reserva in reservas_semanales:
        semana_actual = reserva['semana'].isocalendar()[1]
        semana_index = semana_actual - primera_semana_mes
        if 0 <= semana_index < 5:
            reservas_totales_semanales[semana_index] = reserva['total']

    total_reservas_semana = Reserva.objects.filter(fecha_inicio__range=[inicio_semana, fin_semana]).count()
    canceladas_semana = Reserva.objects.filter(fecha_inicio__range=[inicio_semana, fin_semana], cancelada=True).count()
    tasa_cancelacion_semanal = round((canceladas_semana / total_reservas_semana * 100), 1) if total_reservas_semana > 0 else 0

    reservas_servicio_hoy = ReservaServicio.objects.filter(
        fecha_reservada=hoy, cancelada=False
    ).count()

    servicios_hoy = ReservaServicio.objects.filter(
        fecha_reservada=hoy, pagado=True, cancelada=False
    ).count()

    dashboard_data = json.dumps({
        'semanas': semanas_mes,
        'dias': dias_semana,
        'ingresos_totales_diarios': ingresos_totales_diarios,
        'ingresos_totales_semanales': ingresos_totales_semanales,
        'reservas_totales_diarias': reservas_totales_diarias,
        'reservas_totales_semanales': reservas_totales_semanales,
        'reservas_servicio_hoy': reservas_servicio_hoy,
        'servicios_hoy': servicios_hoy,
        'tasa_cancelacion_diaria':tasa_cancelacion_diaria,
        'tasa_cancelacion_semanal':tasa_cancelacion_semanal,
        'reservas_no_canceladas_hoy': 100 - tasa_cancelacion_diaria,
        'reservas_no_canceladas_semana': 100 - tasa_cancelacion_semanal,
    })
    print(reservas_servicio_hoy,servicios_hoy,hoy)
    return render(request, 'base/admin/dashboard_operativo.html', {'dashboard_data': dashboard_data})


def dashboard_estrategico(request):
    
    hoy = now().date()
    año_actual = now().year
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
    fin_semana = inicio_semana + timedelta(days=6)  # Domingo de la semana actual


    # ===================== Cálculo de Ingresos Diarios =====================
    ingresos_diarios = (
        Reserva.objects.filter(
            pagado=True,  # Solo reservas pagadas
            fecha_inicio=hoy  # Filtra por la fecha actual
        )
        .aggregate(total=Sum('precio_total'))  # Suma los ingresos totales de ese día
    )

    # Asegúrate de que no sea None si no hay ingresos ese día
    ingresos_diarios_total = ingresos_diarios['total'] or 0

    # ===================== Cálculo de Ingresos Mensuales =====================
    ingresos_mensuales = (
        Reserva.objects.filter(pagado=True, fecha_inicio__year=año_actual)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Sum('precio_total'))
        .order_by('mes')
    )

    # Convertir fechas en cadenas
    ingresos_mensuales = [
        {'mes': ingreso['mes'].strftime('%Y-%m'), 'total': ingreso['total']}
        for ingreso in ingresos_mensuales
    ]

    # Inicialización de otras variables para el dashboard
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    ingresos_totales_mensuales = [0] * 12

    for ingreso in ingresos_mensuales:
        mes_index = datetime.strptime(ingreso['mes'], '%Y-%m').month - 1
        ingresos_totales_mensuales[mes_index] = ingreso['total']


    ingresos_mensuales = (
        Reserva.objects.filter(pagado=True, fecha_inicio__year=año_actual)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Sum('precio_total'))
        .order_by('mes')
    )

    # Convertir fechas en cadenas
    ingresos_mensuales = [
        {'mes': ingreso['mes'].strftime('%Y-%m'), 'total': ingreso['total']}
        for ingreso in ingresos_mensuales
    ]

    reservas_mensuales = (
        Reserva.objects.all()
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Inicializar lista de reservas por mes
    total_reservas_mensuales = [0] * 12
    for reserva in reservas_mensuales:
        mes_index = reserva['mes'].month - 1
        total_reservas_mensuales[mes_index] = reserva['total']

    reservas_servicio_mensuales = (
        ReservaServicio.objects.all()
        .annotate(mes=TruncMonth('fecha_reservada'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    reservas_totales_por_mes = [0] * 12  # Inicializar con 0 para cada mes

    # Llenar los datos de reservas mensuales
    for reserva in reservas_servicio_mensuales:
        mes_index = reserva['mes'].month - 1
        reservas_totales_por_mes[mes_index] = reserva['total']

    reservas_por_habitacion = (
        Reserva.objects.all()
        .values('habitacion__tipo_habitacion')
        .annotate(total_reservas=Count('id'))
        .order_by('-total_reservas')
    )
    
    print(reservas_por_habitacion)

    habitaciones = [reserva['habitacion__tipo_habitacion'] for reserva in reservas_por_habitacion]
    total_reservas_habitaciones = [reserva['total_reservas'] for reserva in reservas_por_habitacion]

    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    ingresos_totales_mensuales = [0] * 12

    for ingreso in ingresos_mensuales:
        mes_index = datetime.strptime(ingreso['mes'], '%Y-%m').month - 1
        ingresos_totales_mensuales[mes_index] = ingreso['total']

    crecimiento_mensual_servicio = (
        ReservaServicio.objects.filter(fecha_reservada__year=año_actual,cancelada=False)
        .annotate(mes=TruncMonth('fecha_reservada'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Convertir fechas a cadena en crecimiento_mensual_servicio
    crecimiento_mensual_servicio = [
        {'mes': item['mes'].strftime('%Y-%m'), 'total': item['total']}
        for item in crecimiento_mensual_servicio
    ]
    crecimiento_mensual_habitacion = (
        Reserva.objects.filter(fecha_inicio__year=año_actual,cancelada=False)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Convertir fechas a cadena en crecimiento_mensual_servicio
    crecimiento_mensual_habitacion = [
        {'mes': item['mes'].strftime('%Y-%m'), 'total': item['total']}
        for item in crecimiento_mensual_habitacion
    ]

    # Cálculo de servicios
    reservas_servicio_total = ReservaServicio.objects.count()
    servicios_cancelados = ReservaServicio.objects.filter(cancelada=True).count()
    tasa_cancelacion_servicios = (
        round((servicios_cancelados / reservas_servicio_total * 100), 1)
        if reservas_servicio_total > 0 else 0  # Usamos reservas_servicio_total aquí
    )

    # Cálculo de reservas
    total_reservas = Reserva.objects.count()
    canceladas = Reserva.objects.filter(cancelada=True).count()
    tasa_cancelacion = (
        round((canceladas / total_reservas * 100), 1)
        if total_reservas > 0 else 0
    )

    # ===================== Reservas por Tipo de Servicio =====================
    reservas_por_servicio = (
        ReservaServicio.objects
        .filter(cancelada=False)  # Filtrar solo las no canceladas
        .values('servicio')
        .annotate(total_reservas=Count('id'))
        .order_by('-total_reservas')
    )

    ingresos_por_servicio = (
        ReservaServicio.objects.filter(cancelada=False, pagado=True)
        .values('servicio')
        .annotate(total_ingresos=Sum('precio'))
        .order_by('-total_ingresos')
    )
    
    # Extraer los datos para el gráfico
    tipos_servicio = [reserva['servicio'] for reserva in reservas_por_servicio]
    total_reservas_servicio = [reserva['total_reservas'] for reserva in reservas_por_servicio]
    
    # Extraer los datos para el gráfico
    ingresos_tipos_servicio = [ingreso['servicio'] for ingreso in ingresos_por_servicio]
    ingresos_total_reservas_servicio = [ingreso['total_ingresos'] for ingreso in ingresos_por_servicio]


    ingresos_servicio_mensuales = (
        ReservaServicio.objects.filter(cancelada=False, pagado=True)
        .annotate(mes=TruncMonth('fecha_reservada'))
        .values('mes', 'servicio')
        .annotate(total_ingresos=Sum('precio'))
        .order_by('mes', 'servicio')
    )

    ingresos_por_servicio_mes = {}

    # Inicializar los datos
    for servicio in ingresos_servicio_mensuales:
        mes_index = servicio['mes'].month - 1
        nombre_servicio = servicio['servicio']
        if nombre_servicio not in ingresos_por_servicio_mes:
            ingresos_por_servicio_mes[nombre_servicio] = [0] * 12
        ingresos_por_servicio_mes[nombre_servicio][mes_index] = servicio['total_ingresos']

    # Preparar los datos para enviar al template
    servicios = list(ingresos_por_servicio_mes.keys())
    ingresos_mensuales_por_servicio = list(ingresos_por_servicio_mes.values())
    # Preparación de los datos para la plantilla
    
    dashboard_data = json.dumps({
        'tasa_cancelacion': tasa_cancelacion,
        'tasa_cancelacion_servicios': tasa_cancelacion_servicios,
        'meses':meses,
        'total_reservas_mensuales':total_reservas_mensuales,
        'habitacion_tipos': habitaciones,
        'habitacion_reservas': total_reservas_habitaciones,
        'ingresos_totales_mensuales': ingresos_totales_mensuales,
        'crecimiento_mensual_servicio': list(crecimiento_mensual_servicio),
        'crecimiento_mensual_habitacion':list(crecimiento_mensual_habitacion),
        'reservas_totales_por_mes':reservas_totales_por_mes,
        'tipos_servicio': tipos_servicio,
        'total_reservas_servicio': total_reservas_servicio,
        'ingresos_tipos_servicio':ingresos_tipos_servicio,
        'ingresos_total_reservas_servicio':ingresos_total_reservas_servicio,
        'servicios': servicios,
        'ingresos_mensuales_por_servicio': ingresos_mensuales_por_servicio,
        'fecha_hoy': hoy.strftime('%d-%m-%Y'),  # Convierte la fecha actual a string
        'ingresos_diarios_total': ingresos_diarios_total,  # Enviar el total de ingresos diarios
        'meses': meses,
        'ingresos_totales_mensuales': ingresos_totales_mensuales,
        
    })

    print(total_reservas_habitaciones)  # Depuración

    return render(request, 'base/admin/dashboard_estrategico.html', {
        'dashboard_data': dashboard_data
    })



def listar_regalias(request):
    # Obtener todas las regalías ordenadas por 'id'
    regalias = Regalia.objects.all().order_by('id')  # Ordena por ID para resultados consistentes
    paginator = Paginator(regalias, 5)  # Mostrar 5 regalías por página
    print(regalias)
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
        # Si hay un error en el número de página, redirigir a la primera página
        return redirect('?page=1')
    except EmptyPage:
        # Si la página está fuera de rango, redirigir a la última página
        return redirect(f'?page={paginator.num_pages}')

    contexto = {'page_obj': page_obj}
    return render(request, 'base/admin/regalias.html', context=contexto)

def agregar_regalia(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        foto = request.FILES.get('foto')

        nueva_regalia = Regalia(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            foto=foto
        )
        nueva_regalia.save()
        messages.success(request, 'Regalía agregada exitosamente.')
        return redirect('listar_regalias')
    return redirect('listar_regalias')

def modificar_regalia(request, regalia_id):
    regalia = get_object_or_404(Regalia, id=regalia_id)

    if request.method == 'POST':
        regalia.nombre = request.POST['nombre']
        regalia.descripcion = request.POST['descripcion']
        regalia.precio = request.POST['precio']
        regalia.stock = request.POST['stock']

        # Actuaizar fto
        if 'foto' in request.FILES:
            regalia.foto = request.FILES['foto']

        regalia.save()
        messages.success(request, 'Regalía modificada exitosamente.')
        return redirect('listar_regalias')

    return redirect('listar_regalias')

def eliminar_regalia(request, regalia_id):
    regalia = get_object_or_404(Regalia, id=regalia_id)
    regalia.delete()
    messages.success(request, 'Regalía eliminada exitosamente.')
    return redirect('listar_regalias')

def listar_reservas_admin(request):
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        action = request.POST.get('action')

        # Obtener la reserva correspondiente
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if action == 'checkin':
            reserva.check_in = True
            reserva.checkout = False  # Reinicia checkout al hacer check-in
            messages.success(request, f"Check-in realizado para la reserva {reserva.id}.")
        elif action == 'anular_checkin':
            reserva.check_in = False
            reserva.checkout = False  # Deshabilita checkout también
            messages.warning(request, f"Check-in anulado para la reserva {reserva.id}.")
        elif action == 'checkout':
            if reserva.check_in:  # Solo permite checkout si ya hay check-in
                reserva.checkout = True
                messages.success(request, f"Checkout realizado para la reserva {reserva.id}.")
            else:
                messages.error(request, f"No se puede hacer checkout sin check-in.")
        elif action == 'anular_checkout':
            reserva.checkout = False
            messages.warning(request, f"Checkout anulado para la reserva {reserva.id}.")

        # Guardar los cambios en la reserva
        reserva.save()
        return redirect('listar_reservas_admin')

    # Obtener parámetros de filtro desde la URL
    buscar_cliente = request.GET.get('buscar_cliente', '').strip()
    buscar_habitacion = request.GET.get('buscar_habitacion', '').strip()

    # Filtrar las reservas según el filtro seleccionado
    reservas = Reserva.objects.filter(cancelada=False).order_by('-fecha_inicio')

    if buscar_cliente:
        reservas = reservas.filter(cliente__first_name__icontains=buscar_cliente)
    if buscar_habitacion:
        reservas = reservas.filter(habitacion__numero_habitacion__icontains=buscar_habitacion)

    paginator = Paginator(reservas, 10)

    # Obtener el número de página desde la URL
    page_number = request.GET.get('page', '1')

    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
        page_obj = paginator.get_page(page_number)
    except (ValueError, PageNotAnInteger):
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    contexto = {
        'page_obj': page_obj,
        'buscar_cliente': buscar_cliente,
        'buscar_habitacion': buscar_habitacion,
    }
    return render(request, 'base/admin/listar_reservas_admin.html', context=contexto)



from django.db.models import Count, Q

def listar_trabajadores(request):
    trabajadores = Usuario.objects.filter(trabajador=True).order_by('idUsuario__username')

    paginator = Paginator(trabajadores, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'base/admin/registrar_trabajador.html', {'page_obj': page_obj})



def modificar_trabajador(request, id):
    trabajador = get_object_or_404(Usuario, id=id)
    user = trabajador.idUsuario  

    if request.method == 'POST':
        username = request.POST.get('usuario')
        email = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()  

        trabajador.telefono = telefono
        trabajador.save()  

        sweetify.success(request, 'Trabajador modificado exitosamente.')
    
    return redirect('listar_trabajadores')


def eliminar_trabajador(request, id):
    trabajador = get_object_or_404(Usuario, id=id)
    user = trabajador.idUsuario

    # Liberar reservas asignadas a este trabajador
    Reserva.objects.filter(trabajador=user).update(trabajador=None)

    user.delete()
    sweetify.success(request, 'Trabajador eliminado exitosamente y reservas liberadas.')
    return redirect('listar_trabajadores')



def registrar_trabajador(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        nombre = request.POST.get('first_name', '').strip()
        contrasenia = request.POST.get('contrasenia', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        if not usuario or not nombre or not contrasenia or not correo:
            sweetify.error(request, "Todos los campos son obligatorios.")
            return redirect('listar_trabajadores')

        if User.objects.filter(username=usuario).exists() or Usuario.objects.filter(idUsuario__email=correo).exists():
            sweetify.warning(request, f"El nombre de usuario '{usuario}' o el correo '{correo}' ya están en uso.")
            return redirect('listar_trabajadores')

        try:
            usuario_creado, se_creo = User.objects.get_or_create(
                username=usuario,
                first_name=nombre,
                email=correo
            )

            if not se_creo:
                sweetify.warning(request, 'El usuario ya existe.')
                return redirect('listar_trabajadores')

            usuario_creado.set_password(contrasenia)
            usuario_creado.save()

            trabajador = Usuario.objects.create(
                idUsuario=usuario_creado,
                tipo_cuenta='Trabajador',
                telefono=telefono,
                trabajador=True
            )

            # Asignar automáticamente reservas pendientes al nuevo trabajador
            reservas_pendientes = Reserva.objects.filter(trabajador__isnull=True, cancelada=False)[:10]
            for reserva in reservas_pendientes:
                reserva.trabajador = usuario_creado
                reserva.save()

            sweetify.success(request, "Trabajador registrado correctamente y reservas asignadas.")
            return redirect('listar_trabajadores')

        except Exception as ex:
            sweetify.error(request, f"Error al crear el trabajador: {str(ex)}")
            return redirect('listar_trabajadores')

        
def realizar_check_in(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if not reserva.pagado:
        sweetify.error(request, "No se puede realizar el check-in. La reserva no está pagada.")
        return redirect('listar_reservas_admin')

    # Alternar el estado de check-in
    reserva.check_in = not reserva.check_in
    if reserva.check_in:
        sweetify.success(request, "Check-in realizado con éxito.")
    else:
        sweetify.warning(request, "Check-in cancelado con éxito.")

    reserva.save()
    return redirect('listar_reservas_admin')



def realizar_checkout(request, id):
    """
    Cambia el estado de checkout de la reserva y libera la disponibilidad de la habitación.
    """
    reserva = get_object_or_404(Reserva, id=id)

    # Verificar que el check-in haya sido realizado
    if not reserva.check_in:
        sweetify.error(request, "No se puede realizar el check-out. Aún no se ha hecho el check-in.")
        return redirect('listar_reservas_admin')

    # Marcar como realizado el check-out
    reserva.checkout = True
    reserva.save()

    # Hacer que la habitación esté disponible nuevamente
    habitacion = reserva.habitacion
    habitacion.disponible = True  # Se asume que la habitación se marca como disponible
    habitacion.save()

    sweetify.success(request, "Check-out realizado con éxito.")
    return redirect('listar_reservas_admin')








def recepcion(request):
    # Obtener valores de los filtros desde la URL
    buscar_cliente = request.GET.get('buscar_cliente', '').strip()
    buscar_habitacion = request.GET.get('buscar_habitacion', '').strip()

    # Filtrar reservas no pagadas y no canceladas
    reservas_no_pagadas = Reserva.objects.filter(pagado=False, cancelada=False)

    # Aplicar filtros si están presentes
    if buscar_cliente:
        reservas_no_pagadas = reservas_no_pagadas.filter(cliente__first_name__icontains=buscar_cliente)
    if buscar_habitacion:
        reservas_no_pagadas = reservas_no_pagadas.filter(habitacion__numero_habitacion__icontains=buscar_habitacion)

    # Ordenar las reservas por fecha de inicio
    reservas_no_pagadas = reservas_no_pagadas.order_by('fecha_inicio')

    return render(request, 'base/admin/recepcion.html', {
        'reservas': reservas_no_pagadas,
        'buscar_cliente': buscar_cliente,
        'buscar_habitacion': buscar_habitacion,
    })





########################### NUEVO

def marcar_como_pagada(request, reserva_id):
    try:
        # Obtener la reserva
        reserva = get_object_or_404(Reserva, id=reserva_id)
        # Marcar la reserva como pagada
        reserva.pagado = True
        reserva.save()
        # Agregar URL absoluta para la imagen de la mascota (si existe)
        if reserva.mascota.imagen_mascota:
            reserva.mascota.imagen_mascota_url = request.build_absolute_uri(reserva.mascota.imagen_mascota.url)
        else:
            reserva.mascota.imagen_mascota_url = None
        # Contexto para el PDF
        context = {
            'reserva': reserva,
            'precio_total': reserva.calcular_precio_total(),
        }
        # Cargar la plantilla del PDF
        template = get_template('base/admin/boleta.html')  # Plantilla tipo boleta
        html = template.render(context)
        # Generar el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="boleta_reserva_{reserva_id}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=400)
        return response
    
    
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)