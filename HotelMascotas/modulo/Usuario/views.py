from datetime import datetime, timedelta, date
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
import re
import sweetify

from modulo.Usuario.models import Usuario, ReservaServicio, Calificacion, Mensaje
from modulo.Producto.models import Habitacion, Reserva, Membresia, ReservaRegalia
from modulo.Colaborador.models import Colaborador, Disponibilidad
from .forms import FichaSaludForm
from .models import Ficha


def modificar_mascota(request, id_mascota):
    mascota = get_object_or_404(Ficha, id=id_mascota)

    if request.method == 'POST':
        # Actualizar los campos de texto
        mascota.nombre_perro = request.POST.get('nombre_perro')
        mascota.raza = request.POST.get('raza')
        mascota.edad = request.POST.get('edad')
        mascota.peso = request.POST.get('peso')
        mascota.chip = request.POST.get('chip')
        mascota.comida = request.POST.get('comida')

        # Combinar las nuevas selecciones con las existentes para vacunas, alergias y enfermedades
        nuevas_vacunas = set(request.POST.getlist('vacunas'))
        nuevas_alergias = set(request.POST.getlist('alergias'))
        nuevas_enfermedades = set(request.POST.getlist('enfermedades'))

        # Si ya hay valores previos, combínalos con los nuevos valores
        vacunas_actuales = set(mascota.vacunas.split(', ')) if mascota.vacunas else set()
        alergias_actuales = set(mascota.alergias.split(', ')) if mascota.alergias else set()
        enfermedades_actuales = set(mascota.enfermedades.split(', ')) if mascota.enfermedades else set()

        # Unir los conjuntos para mantener valores únicos
        mascota.vacunas = ', '.join(vacunas_actuales.union(nuevas_vacunas))
        mascota.alergias = ', '.join(alergias_actuales.union(nuevas_alergias))
        mascota.enfermedades = ', '.join(enfermedades_actuales.union(nuevas_enfermedades))

        # Procesar la imagen si se ha subido una nueva
        if 'imagen_mascota' in request.FILES:
            mascota.imagen_mascota = request.FILES['imagen_mascota']

        # Guardar los cambios en la base de datos
        mascota.save()
        sweetify.success(request,'Ficha modificada correctamente.')
        return redirect('listar_fichas')

    return render(request, 'base/usuario/listar_fichas.html', {'mascota': mascota})

def eliminar_vacunas(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    ficha.vacunas = ''
    ficha.save()
    sweetify.success(request, 'Vacunas eliminadas.')
    return redirect('listar_fichas')

def eliminar_alergias(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    ficha.alergias = ''
    ficha.save()
    sweetify.success(request, 'Alergias eliminadas.')
    return redirect('listar_fichas')

def eliminar_enfermedades(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    ficha.enfermedades = ''
    ficha.save()
    sweetify.success(request, 'Enfermedades eliminadas.')
    return redirect('listar_fichas')

def principal(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(numero_habitacion__icontains=buscar)
    contexto = {
        'productos': productos
    }
    return render(request, 'base/usuario/caso.html', context=contexto)

def principalUsuario (request):
    
    productos = Habitacion.objects.all()
    membresias = Membresia.objects.all()
    usuario = Usuario.objects.get(idUsuario=request.user)
    mascotas = Ficha.objects.filter(id_usuario=usuario)

    contexto = {
        'productos':productos,
        'mascotas':mascotas,
        'membresias':membresias,
    }
    
    buscar = request.GET.get("buscar", "")
    if request.method == "GET" and buscar:
        productos = Habitacion.objects.filter(numero_habitacion__contains=buscar)
        
        membresias = Membresia.objects.all()
        contexto["productos"] = productos
        contexto["membresias"] = membresias
    return render(request,'base/usuario/casoUsuario.html',context = contexto)


def perfil(request):
    user = request.user
    usuario = get_object_or_404(Usuario, idUsuario=user)
    
    if not usuario.membresia:
        sweetify.toast(request, 'No tienes membresia activa!',icon='warning')

    fichas_usuario = Ficha.objects.filter(id_usuario=usuario)
    reservas_servicio_count = ReservaServicio.objects.filter(mascota__in=fichas_usuario).count()

    reservas_habitacion_count = Reserva.objects.filter(
        cliente=user,
        cancelada=False  # Filtrar solo reservas no canceladas
    ).count()

    fichas_count = fichas_usuario.count()
    print(reservas_servicio_count)
    contexto = {
        'reservas_servicio_count': reservas_servicio_count,
        'reservas_habitacion_count': reservas_habitacion_count,
        'fichas_count': fichas_count,
    }

    return render(request, 'base/usuario/perfil.html', contexto)

def actualizar_perfil(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    
    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        
        try:
            usuario.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        except ValueError:
            sweetify.error(request, 'Fecha de nacimiento no válida. Use el formato AAAA-MM-DD.')
            return redirect('actualizar_perfil') 
        
        usuario.telefono = telefono
        usuario.direccion = direccion
        usuario.save()

        sweetify.success(request, 'Perfil actualizado exitosamente.')
        return redirect('perfil') 

    return render(request, 'base/usuario/datos_perfil.html', {'usuario': usuario})


def listar_reservas_view(request):
    reservas = Reserva.objects.filter(cliente=request.user, cancelada=False)

    reservas_activas = reservas.filter(check_in=True, checkout=False)
    reservas_finalizadas = reservas.filter(checkout=True)
    otras_reservas = reservas.exclude(id__in=reservas_activas | reservas_finalizadas)

    context = {
        'reservas_activas': reservas_activas,
        'reservas_finalizadas': reservas_finalizadas,
        'otras_reservas': otras_reservas,
    }
    return render(request, 'base/usuario/listar_reservas.html', context)

def eliminar_reserva_habitacion(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    reserva.cancelada = True
    reserva.save()  

    sweetify.success(request, 'Reserva cancelada con éxito')
    return redirect('listar_reservas')

    
def ficha_salud_view(request):
    if request.method == 'POST':
        form = FichaSaludForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False) 
            usuario = Usuario.objects.get(idUsuario=request.user)  
            form.id_usuario = usuario  
            form.save()
            sweetify.success(request, 'Se guardo la ficha de su mascota correctamente')
            return render(request,'base/usuario/perfil.html')  
    else:
        form = FichaSaludForm()
    return render(request, 'base/usuario/ficha.html', {'form': form})

def listar_fichas_view(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    fichas = Ficha.objects.filter(id_usuario=usuario)
    print(fichas)
    return render(request, 'base/usuario/listar_fichas.html', {'fichas': fichas})

def editar_ficha_view(request, pk):
    ficha = get_object_or_404(Ficha, pk=pk)  
    if request.method == 'POST':
        form = FichaSaludForm(request.POST, request.FILES, instance=ficha)
        if form.is_valid():
            form.save() 
            return redirect('listar_fichas')  
    else:
        form = FichaSaludForm(instance=ficha)  
        form.fields['nombre_dueno'].widget.attrs['readonly'] = True
    return render(request, 'base/usuario/editar_ficha.html', {'form': form})

def eliminar_ficha(request, id):
    ficha = get_object_or_404(Ficha, id=id)

    reservas_asociadas = Reserva.objects.filter(mascota=ficha).exists()

    if reservas_asociadas:
        sweetify.error(request, 'Cancela la reserva asociada a la mascota para poder eliminarla')
        return redirect('perfil')

    ficha.delete()
    sweetify.success(request, 'Ficha eliminada con éxito.')
    return redirect('perfil')

def generar_pdf_fichas(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    fichas = Ficha.objects.filter(id_usuario=usuario)

    for ficha in fichas:
        if ficha.imagen_mascota:
            ficha.imagen_mascota_url = request.build_absolute_uri(ficha.imagen_mascota.url)
        else:
            ficha.imagen_mascota_url = None

    template = get_template('base/usuario/pdf_ficha.html')
    html = template.render({'fichas': fichas})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fichas_mascotas.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    return response

def registrarse(request):
    if request.method == 'GET':
        return render(request, 'base/Registrarse.html')

    elif request.method == 'POST':
        usuario = request.POST['usuario']
        nombre = request.POST['first_name']
        contrasenia = request.POST['contrasenia']
        correo = request.POST['correo']

        if User.objects.filter(username=usuario).exists() or Colaborador.objects.filter(username=usuario).exists():
            sweetify.warning(request, f"El nombre de usuario '{usuario}' ya está en uso.")
            return render(request, 'base/Registrarse.html')

        try:
            usuario_creado, se_creo = User.objects.get_or_create(
                username=usuario,
                first_name = nombre,
                password = contrasenia,
                email=correo
            )
            
            if not se_creo:
                sweetify.warning(request, 'El usuario ya existe')
                return render(request, 'base/Registrarse.html')

            usuario_creado.set_password(contrasenia)
            usuario_creado.save()

            nuevoUsuario = Usuario()
            nuevoUsuario.idUsuario = usuario_creado
            nuevoUsuario.tipo_cuenta = 'Usuario'
            nuevoUsuario.save()
            sweetify.success(request, f"Usuario registrado correctamente")
            return HttpResponseRedirect(reverse('iniciarsesion'))

        except Exception as ex:
            sweetify.warning(request, f"Error al crear el usuario: {str(ex)}")
            return render(request, 'base/Registrarse.html')

    return render(request, 'base/Registrarse.html')
       
def iniciarsesion(request):
    if request.method == 'GET':
        return render(request, 'base/IniciarSesion.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        usuario_encontrado = authenticate(username=usuario, password=contrasenia)
        if usuario_encontrado is not None:
            login(request, usuario_encontrado)
            if usuario_encontrado.is_superuser:
                sweetify.toast(request,f'Bienvenido {usuario_encontrado.first_name}',position='top-start')
                return redirect('dashboard_admin') 
            else:
                sweetify.toast(request,f'Bienvenido {usuario_encontrado.first_name}',position='top-start')
                return redirect('principalUsuario')  
        else:
            sweetify.error(request, 'Usuario o Contraseña incorrecto')
            return render(request, 'base/IniciarSesion.html')

def cerrar_sesion(request):
    if request.user.is_authenticated:
        logout(request)

    storage = messages.get_messages(request)
    for message in storage:
        message.used = True
    sweetify.toast(request,'Sesion cerrada con exito',position='top-start')
    return HttpResponseRedirect(reverse('principal'))

def reservas_hotel(request, habitacion_id):
    # Obtener la habitación
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)

    # Filtrar las reservas de la habitación excluyendo las que ya tienen checkout
    reservas = Reserva.objects.filter(
        habitacion=habitacion,
        cancelada=False,  # Excluir reservas canceladas
        checkout=False    # Excluir reservas con checkout realizado
    )

    # Preparar los datos de las reservas para pasarlos al frontend (si necesario)
    eventos = [
        {
            'title': f'Habitación {reserva.habitacion.numero_habitacion}',
            'start': reserva.fecha_inicio.strftime('%Y-%m-%d'),
            'end': (reserva.fecha_fin + timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        for reserva in reservas
    ]

    # Contexto para renderizar la vista
    contexto = {
        'habitacion_id': habitacion_id,
        'habitacion': habitacion,
        'eventos': eventos,  # Incluye los datos para el calendario si se necesita
    }
    return render(request, 'base/usuario/reservas_hotel.html', contexto)


def ver_horas_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    disponibilidades = Disponibilidad.objects.filter(colaborador=colaborador, disponible=True)
    usuario = Usuario.objects.get(idUsuario=request.user)
    mascotas = Ficha.objects.filter(id_usuario=usuario)
    contexto = {
        'colaborador': colaborador,
        'disponibilidades': disponibilidades,
        'mascotas':mascotas
    }
    return render(request, 'base/usuario/ver_horas_colaborador.html', contexto)



def servicios_disponibles(request):
    servicio_filtrado = request.GET.get('servicio')  
    if servicio_filtrado:
        servicios = Colaborador.objects.filter(servicio=servicio_filtrado)
    else:
        servicios = Colaborador.objects.all()
    contexto = {
        'servicios': servicios
    }

    return render(request, 'base/usuario/servicios_disponibles.html', contexto)

from datetime import datetime, time

def reservar_servicio(request):
    if request.method == 'POST':
        mascota_id = request.POST.get('mascota_id')
        colaborador_id = request.POST.get('colaborador_id')
        servicio = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fin_str = request.POST.get('hora_fin')

        fecha_reservada = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

        
        colaborador = get_object_or_404(Colaborador, id=colaborador_id)
        mascota = get_object_or_404(Ficha, id=mascota_id)

       
        reserva_existente = ReservaServicio.objects.filter(
            colaborador=colaborador,
            servicio=servicio,
            fecha_reservada=fecha_reservada,
            hora_inicio__lt=hora_fin,  
            hora_fin__gt=hora_inicio   
        ).exists()

        if reserva_existente:
            sweetify.error(request, f'Ya existe una reserva de servicio para {mascota.nombre_perro} en ese rango de horas.')
            return redirect('servicios_disponibles')

        disponibilidad = Disponibilidad.objects.filter(
            colaborador=colaborador,
            servicio=servicio,
            fecha=fecha_reservada,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
            disponible=True
        ).first()

        if not disponibilidad:
            sweetify.error(request, f'El colaborador no tiene disponibilidad en ese horario.')
            return redirect('servicios_disponibles')

        nueva_reserva = ReservaServicio.objects.create(
            colaborador=colaborador,
            servicio=servicio,
            fecha_reservada=fecha_reservada,
            mascota=mascota,
            precio=colaborador.precio_por_hora,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )

        disponibilidad.disponible = False
        disponibilidad.save()

        sweetify.success(request, f"¡Reserva de servicio realizada con éxito para el {nueva_reserva.fecha_reservada}!")
        return redirect('servicios_disponibles')
    
    return redirect('servicios_disponibles')


def listar_reservas_servicios(request):
    usuario = request.user
    mascotas_usuario = Ficha.objects.filter(id_usuario__idUsuario=usuario)


    reservas_pagadas = ReservaServicio.objects.filter(mascota__in=mascotas_usuario, pagado=True)
    reservas_no_pagadas = ReservaServicio.objects.filter(mascota__in=mascotas_usuario, pagado=False)
    print(reservas_pagadas)
    contexto = {
        'reservas_pagadas': reservas_pagadas,
        'reservas_no_pagadas': reservas_no_pagadas
    }

    return render(request, 'base/usuario/listar_reservas_servicio.html', contexto)

def eliminar_reserva_servicio(request, reserva_id):
    usuario = get_object_or_404(Usuario, idUsuario=request.user)
    mascotas_usuario = Ficha.objects.filter(id_usuario=usuario)
    reserva = get_object_or_404(ReservaServicio, id=reserva_id, mascota__in=mascotas_usuario)

    disponibilidad = Disponibilidad.objects.filter(
        colaborador=reserva.colaborador,
        servicio=reserva.servicio,
        fecha=reserva.fecha_reservada,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin
    ).first()

    if disponibilidad:
        disponibilidad.disponible = True
        disponibilidad.save()

    reserva.delete()
    sweetify.success(request, 'Reserva de servicio eliminada con éxito')
    return redirect('listar_reservas_servicios')

def unirse_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    perfil_usuario = Usuario.objects.get(idUsuario=request.user)

    # Verificar si el usuario ya tiene una membresía activa
    if perfil_usuario.membresia and perfil_usuario.fecha_inicio_membresia:
        fecha_vencimiento = perfil_usuario.fecha_inicio_membresia + timedelta(days=perfil_usuario.membresia.duracion_dias)
        hoy = date.today()

        if hoy >= fecha_vencimiento:
            # La membresía ha caducado, eliminarla
            perfil_usuario.membresia = None
            perfil_usuario.fecha_inicio_membresia = None
            perfil_usuario.save()
            sweetify.info(request, 'Tu membresía anterior ha caducado. Ahora puedes unirte a una nueva.')
        else:
            sweetify.warning(request, 'Ya tienes una membresía activa. Espera a que caduque para unirte a otra.')
            return redirect('gestionar_membresia_usuario')

    if request.method == 'POST':
        return redirect('iniciar_pago', item_id=membresia.id, tipo_pago='membresia')

    return render(request, 'base/usuario/membresia_confirmacion.html', {'membresia': membresia})



def gestionar_membresia_usuario(request):
    try:
        perfil_usuario = Usuario.objects.get(idUsuario=request.user)
        membresia = perfil_usuario.membresia  
    except Usuario.DoesNotExist:
        membresia = None

    return render(request, 'base/usuario/listar_membresia.html', {
        'membresia': membresia,
    })

def cambiar_membresia(request):
    membresias = Membresia.objects.all()  

    if request.method == 'POST':
        nueva_membresia_id = request.POST.get('membresia_id')
        nueva_membresia = Membresia.objects.get(id=nueva_membresia_id)

        perfil_usuario = Usuario.objects.get(idUsuario=request.user)
        perfil_usuario.membresia = nueva_membresia
        perfil_usuario.save()

        messages.success(request, 'Has cambiado de membresía exitosamente.')
        return redirect('gestionar_membresia_usuario')

    return render(request, 'base/usuario/cambiar_membresia.html', {
        'membresias': membresias,
    })


def cancelar_membresia(request):
    perfil_usuario = Usuario.objects.get(idUsuario=request.user)
    perfil_usuario.membresia = None  
    perfil_usuario.save()

    sweetify.success(request, 'Has cancelado tu membresía.')
    return redirect('gestionar_membresia_usuario')


def agregar_calificacion(request):
    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        calificacion = int(request.POST.get('calificacion'))
        Calificacion.objects.create(
            usuario=request.user,
            comentario=comentario,
            calificacion=calificacion
        )
        messages.success(request, '¡Gracias por tu calificación!')
    calificaciones = Calificacion.objects.all().order_by('-fecha_creacion')
    return render(
        request,
        'base/usuario/calificacion.html',
        {'calificaciones': calificaciones, 'rango_estrellas': range(1, 6)}
    )
    
def eliminar_calificacion(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id, usuario=request.user)
    calificacion.delete()
    messages.success(request, 'Tu calificación ha sido eliminada.')
    return redirect('agregar_calificacion') 



def mostrar_calificacion(request):
    calificacions = Calificacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'inicio.html', {'calificacions': calificacions})

def enviar_calificacion(request):
    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        calificacion = int(request.POST.get('calificacion'))

        nueva_calificacion = Calificacion.objects.create(
            usuario=request.user,
            comentario=comentario,
            calificacion=calificacion
        )

        messages.success(request, '¡Gracias por tu calificación!')
        return redirect('agregar_calificacion') 
    return render(request, 'calificacion.html')

def listar_calificaciones(request):
    calificaciones = Calificacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'inicio_cliente.html', {'calificaciones': calificaciones})

def generar_pdf_reserva(request, reserva_id):
    try:
        reserva = Reserva.objects.get(id=reserva_id)
    except Reserva.DoesNotExist:
        return HttpResponse('Reserva no encontrada', status=404)

    if reserva.mascota.imagen_mascota:
        reserva.mascota.imagen_mascota_url = request.build_absolute_uri(reserva.mascota.imagen_mascota.url)
    else:
        reserva.mascota.imagen_mascota_url = None

    context = {
        'reserva': reserva,
        'precio_total': reserva.calcular_precio_total()  
    }


    template = get_template('base/usuario/pdf_reserva.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reserva_{reserva_id}.pdf"'


    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    
    return response

def regalos(request):
    # Obtener el usuario autenticado
    usuario = request.user

    # Filtrar las ReservaRegalia que cumplan con las condiciones
    regalos_pendientes = ReservaRegalia.objects.filter(cliente=usuario, usada=True, pagada=False)
    regalos_pagados = ReservaRegalia.objects.filter(cliente=usuario, usada=True, pagada=True) #pagadas

    total_pendiente = sum(regalo.precio_total_r for regalo in regalos_pendientes)
    total_pagado = sum(regalo.precio_total_r for regalo in regalos_pagados)

    # Obtener los IDs de las reservas asociadas a las ReservaRegalia seleccionadas
    reservas_ids = regalos_pendientes.values_list('reserva_id', flat=True)
    reservas_ids_pagadas = regalos_pagados.values_list('reserva_id', flat=True) #pagadas

    # Filtrar las reservas de habitaciones relacionadas que tengan checkout=True
    reservas_finalizadas = Reserva.objects.filter(id__in=reservas_ids, checkout=True)
    reservas_pagadas = Reserva.objects.filter(id__in=reservas_ids_pagadas, checkout=True) #pagadas
        
    # Pasar los datos al contexto
    context = {
        'regalos_pendientes': regalos_pendientes,
        'reservas_finalizadas': reservas_finalizadas,
        'reservas_pagadas': reservas_pagadas,
        'total_pendiente': total_pendiente,
        'total_pagado': total_pagado,
    }
    print(context)

    return render(request, 'base/usuario/regalos.html', context)




def prueba(request):
    return render(request, 'base/prueba.html')