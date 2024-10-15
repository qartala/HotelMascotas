from datetime import datetime, timedelta, time
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from modulo.Producto.models import Habitacion, Reserva
from modulo.Colaborador.models import Colaborador, Disponibilidad
from modulo.Usuario.models import Usuario, ReservaServicio
from modulo.Producto.models import Membresia
from django.template.loader import get_template
from xhtml2pdf import pisa
import re
import sweetify
from .forms import FichaSaludForm
from .models import Ficha



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
    # Obtener el usuario autenticado
    user = request.user
    
    # Obtener el objeto Usuario asociado al User
    usuario = get_object_or_404(Usuario, idUsuario=user)

    # Contar las reservas de servicios asociadas a las fichas del usuario
    fichas_usuario = Ficha.objects.filter(id_usuario=usuario)
    reservas_servicio_count = ReservaServicio.objects.filter(mascota__in=fichas_usuario).count()

    # Contar las reservas de habitaciones asociadas al usuario
    reservas_habitacion_count = Reserva.objects.filter(cliente=user).count()

    # Contar las fichas de animales asociadas al usuario
    fichas_count = fichas_usuario.count()

    contexto = {
        'reservas_servicio_count': reservas_servicio_count,
        'reservas_habitacion_count': reservas_habitacion_count,
        'fichas_count': fichas_count,
    }

    return render(request, 'base/usuario/perfil.html', contexto)


def listar_reservas_view(request):
    reservas = Reserva.objects.filter(cliente=request.user)  # O como obtengas las reservas

    # Filtrar reservas por pagado y no pagado
    reservas_por_pagar = reservas.filter(pagado=False)
    reservas_pagadas = reservas.filter(pagado=True)

    # Pasar los resultados al contexto
    context = {
        'reservas_por_pagar': reservas_por_pagar,
        'reservas_pagadas': reservas_pagadas,
    }
    return render(request, 'base/usuario/listar_reservas.html', context)

def eliminar_reserva_habitacion(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    reserva.delete()
    sweetify.success(request, 'Reserva eliminada con éxito')
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
    # Obtener la ficha de la mascota
    ficha = get_object_or_404(Ficha, id=id)

    # Verificar si la mascota está asociada a una reserva de habitación
    reservas_asociadas = Reserva.objects.filter(mascota=ficha).exists()

    if reservas_asociadas:
        # Si hay reservas asociadas, mostrar un mensaje de error y evitar la eliminación
        sweetify.error(request, 'Cancela la reserva asociada a la mascota para poder eliminarla')
        return redirect('perfil')

    # Si no hay reservas asociadas, se puede eliminar la ficha
    ficha.delete()
    sweetify.success(request, 'Ficha eliminada con éxito.')
    return redirect('perfil')

def generar_pdf_fichas(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    fichas = Ficha.objects.filter(id_usuario=usuario)

    # Genera las URLs absolutas para las imágenes
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
                return redirect('vistaAdmin') 
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
        habitacion = get_object_or_404(Habitacion, id=habitacion_id)
        print(habitacion)
        contexto = {
            'habitacion_id': habitacion_id,
            'habitacion': habitacion
        }
        return render(request,'base/usuario/reservas_hotel.html', contexto)

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
        fecha = request.POST.get('fecha')  # Se obtiene como string, lo convertimos a fecha
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fin_str = request.POST.get('hora_fin')

        # Convertir fecha y hora a objetos datetime y time
        fecha_reservada = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

        # Obtener el colaborador y la mascota
        colaborador = get_object_or_404(Colaborador, id=colaborador_id)
        mascota = get_object_or_404(Ficha, id=mascota_id)

        # Verificar si existe una reserva de habitación para esa mascota y fecha
        reserva_habitacion = Reserva.objects.filter(
            mascota=mascota,
            fecha_inicio__lte=fecha_reservada,  # Fecha reservada debe estar entre fecha_inicio y fecha_fin
            fecha_fin__gte=fecha_reservada
        ).first()  # Usamos .first() para obtener una sola reserva, si existe

        if not reserva_habitacion:
            # Si no existe una reserva de habitación, mostramos un mensaje de error
            sweetify.error(request, f'El horario del colaborador no coincide con tus reservas realizadas para {mascota.nombre_perro}(mascota)')
            return redirect('servicios_disponibles')    

        # Verificar si ya existe una reserva de servicio para el mismo colaborador, servicio, fecha y mascota
        reserva_existente = ReservaServicio.objects.filter(
            colaborador=colaborador,
            servicio=servicio,
            fecha_reservada=fecha_reservada,
            mascota=mascota,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        ).exists()

        if reserva_existente:
            sweetify.error(request, f'Ya existe una reserva de servicio para {mascota.nombre_perro} en esa fecha y hora.')
            return redirect('servicios_disponibles')

        # Crear la reserva de servicio
        nueva_reserva = ReservaServicio.objects.create(
            colaborador=colaborador,
            servicio=servicio,
            fecha_reservada=fecha_reservada,
            mascota=mascota,
            precio=colaborador.precio_por_hora,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )

        # Marcar la disponibilidad como no disponible
        disponibilidad = Disponibilidad.objects.filter(
            colaborador=colaborador,
            servicio=servicio,
            fecha=fecha_reservada,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        ).first()

        if disponibilidad:
            disponibilidad.disponible = False
            disponibilidad.save()

        sweetify.success(request, f"¡Reserva de servicio realizada con éxito para el {nueva_reserva.fecha_reservada}!")
        return redirect('servicios_disponibles')
    
    return redirect('servicios_disponibles')


def listar_reservas_servicios(request):
    # Obtener el usuario autenticado
    usuario = request.user

    # Obtener las mascotas asociadas al usuario
    mascotas_usuario = Ficha.objects.filter(id_usuario__idUsuario=usuario)

    # Filtrar las reservas de servicio asociadas a las mascotas del usuario
    reservas_pagadas = ReservaServicio.objects.filter(mascota__in=mascotas_usuario, pagado=True)
    reservas_no_pagadas = ReservaServicio.objects.filter(mascota__in=mascotas_usuario, pagado=False)

    # Contexto para pasar al template
    contexto = {
        'reservas_pagadas': reservas_pagadas,
        'reservas_no_pagadas': reservas_no_pagadas
    }

    return render(request, 'base/usuario/listar_reservas_servicio.html', contexto)

def eliminar_reserva_servicio(request, reserva_id):
    # Obtener la instancia del modelo Usuario relacionado con el usuario autenticado
    usuario = get_object_or_404(Usuario, idUsuario=request.user)

    # Obtener las fichas (mascotas) asociadas al usuario autenticado
    mascotas_usuario = Ficha.objects.filter(id_usuario=usuario)

    # Buscar la reserva que pertenece a una de las mascotas del usuario
    reserva = get_object_or_404(ReservaServicio, id=reserva_id, mascota__in=mascotas_usuario)

    # Buscar la disponibilidad asociada a la reserva y marcarla como disponible nuevamente
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

    # Eliminar la reserva
    reserva.delete()
    sweetify.success(request, 'Reserva de servicio eliminada con éxito')
    return redirect('listar_reservas_servicios')


def unirse_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    perfil_usuario = Usuario.objects.get(idUsuario=request.user)

    if perfil_usuario.membresia:
        # Redirigir a la página de gestión de membresías si ya tiene una activa
        sweetify.warning(request, 'Ya tienes una membresía activa. Por favor, cancélala antes de unirte a otra.')
        return redirect('gestionar_membresia_usuario')  # O cualquier página de gestión de membresías

    if request.method == 'POST':
        # Iniciar el proceso de pago de la membresía
        return redirect('iniciar_pago', item_id=membresia.id, tipo_pago='membresia')

    # Si es un GET o el usuario aún no ha confirmado, mostramos la página de confirmación
    return render(request, 'base/usuario/membresia_confirmacion.html', {'membresia': membresia})


def gestionar_membresia_usuario(request):
    try:
        perfil_usuario = Usuario.objects.get(idUsuario=request.user)
        membresia = perfil_usuario.membresia  # Membresía confirmada del usuario
    except Usuario.DoesNotExist:
        membresia = None

    return render(request, 'base/usuario/listar_membresia.html', {
        'membresia': membresia,
    })

def cambiar_membresia(request):
    membresias = Membresia.objects.all()  # Listar todas las membresías disponibles

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
    perfil_usuario.membresia = None  # Cancelar la membresía actual
    perfil_usuario.save()

    sweetify.success(request, 'Has cancelado tu membresía.')
    return redirect('gestionar_membresia_usuario')








def prueba(request):
    return render(request, 'base/prueba.html')