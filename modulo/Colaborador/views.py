from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from modulo.Colaborador.models import Colaborador, Disponibilidad
from modulo.Usuario.models import ReservaServicio
import re
import sweetify
from django.core.exceptions import ValidationError
from .forms import DisponibilidadForm, PerfilColaboradorForm
from .models import Disponibilidad
from .decorators import colaborador_required, colaborador_login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.

def colaborador(request):
        return render(request, 'base/colaborador/colaborador.html')

def listar_colaboradores(request):
    colaborador = Colaborador.objects.all()
    contexto = {
        'colaborador': colaborador
    }
    return render(request, 'base/solicitudes.html', context=contexto)

@colaborador_required
def horas_disponibles(request):
    colaborador_id = request.session.get('colaborador_id')

    if not colaborador_id:
        return redirect('iniciarsesionColaborador')

    colaborador = Colaborador.objects.get(id=colaborador_id)

    hoy = datetime.now().date()
    en_30_dias = hoy + timedelta(days=30)

    # Obtener las reservas dentro del rango de 30 días
    reservas = Disponibilidad.objects.filter(colaborador=colaborador, fecha__range=[hoy, en_30_dias])

    # Configurar la paginación para mostrar 5 reservas por página
    paginator = Paginator(reservas, 5)  
    page_number = request.GET.get('page', 1)  # Obtener el número de página de la solicitud

    try:
        # Validar que el número de página sea un entero positivo
        page_number = int(page_number)
        if page_number < 1:
            raise ValueError("El número de página no puede ser menor que 1.")

        # Obtener la página solicitada
        page_obj = paginator.get_page(page_number)

    except (ValueError, PageNotAnInteger):
        # Si el número de página no es válido, redirigir a la primera página
        return redirect('?page=1')
    except EmptyPage:
        # Si la página solicitada está fuera del rango, redirigir a la última página
        return redirect(f'?page={paginator.num_pages}')

    # Contexto para renderizar la plantilla
    contexto = {
        'page_obj': page_obj,
        'colaborador': colaborador,
    }

    return render(request, 'base/colaborador/horas_disponibles.html', context=contexto)


@colaborador_required
def registrar_disponibilidad(request):
    colaborador_id = request.session.get('colaborador_id')

    if not colaborador_id:
        return redirect('iniciarsesionColaborador') 

    colaborador = Colaborador.objects.get(id=colaborador_id)  
    
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST)
        if form.is_valid():
            disponibilidad = form.save(commit=False)
            disponibilidad.colaborador = colaborador

            if not colaborador.servicio:
                form.add_error(None, "El colaborador no tiene un servicio asignado.")
            else:
                disponibilidad.servicio = colaborador.servicio  

                # Verificación de conflicto con el rango de horas
                conflicto = Disponibilidad.objects.filter(
                    colaborador=colaborador,
                    servicio=disponibilidad.servicio,
                    fecha=disponibilidad.fecha
                ).filter(
                    hora_inicio__lt=disponibilidad.hora_fin,  # Verificar si la hora de inicio es menor que la hora de fin de otra disponibilidad
                    hora_fin__gt=disponibilidad.hora_inicio   # Verificar si la hora de fin es mayor que la hora de inicio de otra disponibilidad
                ).exists()

                if conflicto:
                    form.add_error(None, "Ya has registrado una disponibilidad para este horario.")
                else:
                    disponibilidad.save()
                    return redirect('horas_disponibles') 
    else:
        form = DisponibilidadForm()

    contexto = {
        'form': form,
        'colaborador': colaborador,  
    }

    return render(request, 'base/colaborador/horario_disponible.html', contexto)

@colaborador_required
def perfil_colaborador(request):
    colaborador_id = request.session.get('colaborador_id')

    if not colaborador_id:
        return redirect('iniciarsesionColaborador')

    colaborador = Colaborador.objects.get(id=colaborador_id)

    if request.method == 'POST':
        form = PerfilColaboradorForm(request.POST, request.FILES, instance=colaborador)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Perfil actualizado correctamente.', icon='success', timer=3000)
            return redirect('perfil_colaborador')  
        else:
            sweetify.error(request, 'Por favor, corrige los errores en el formulario.', icon='error', timer=3000)
    else:
        form = PerfilColaboradorForm(instance=colaborador)

    contexto = {
        'colaborador': colaborador,
        'form': form
    }

    return render(request, 'base/colaborador/perfil_colaborador.html', contexto)


def registro_colaborador(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        phone_digits = request.POST.get('phone')  
        email = request.POST.get('email')
        password = request.POST.get('password')
        servicio = request.POST.get('service')
        pdf_file = request.FILES.get('pdf_file')

        phone = '+569' + phone_digits

        if len(fullname) > 100:
            sweetify.toast(request, 'El nombre completo no puede tener más de 100 caracteres.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if len(username) > 15:
            sweetify.toast(request, 'El nombre de usuario no puede tener más de 15 caracteres.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[.-]).{1,15}$', username):
            sweetify.toast(request, 'El nombre de usuario debe contener al menos una mayúscula, un número y un punto o guion.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if Colaborador.objects.filter(username=username).exists():
            sweetify.toast(request, f"El nombre de usuario '{username}' ya está en uso.",icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if not re.match(r'^\d{8}$', phone_digits):
            sweetify.toast(request, 'El número de teléfono debe tener el formato +56 9 y luego 8 dígitos.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            sweetify.toast(request, 'Introduce una dirección de correo válida.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if Colaborador.objects.filter(email=email).exists():
            sweetify.toast(request, f"El correo electrónico '{email}' ya está en uso.",icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if len(password) > 15:
            sweetify.toast(request, 'La contraseña no puede tener más de 15 caracteres.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        if not re.match(r'^(?=.*[A-Z]).{1,15}$', password):
            sweetify.toast(request, 'La contraseña debe contener al menos una letra mayúscula.',icon='error', position='center', timer=5000)
            return render(request, 'base/colaborador/registro_colaborador.html', {
                'fullname': fullname,
                'username': username,
                'phone': phone,
                'email': email,
                'servicio': servicio
            })

        try:
            colaborador = Colaborador(
                fullname=fullname,
                username=username,
                phone=phone,
                email=email,
                servicio=servicio,
                pdf_file=pdf_file
            )

            colaborador.set_password(password)
            colaborador.save()
            sweetify.success(request, 'Registro exitoso. Espera la confirmación del administrador.')
            return redirect('colaborador')
        except ValidationError as e:
            sweetify.error(request, f'Error al registrar el colaborador: {str(e)}')
            return render(request, 'base/colaborador/registro_colaborador.html')

    return render(request, 'base/colaborador/registro_colaborador.html')

def verificar_correo(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(email=email).exists() or Colaborador.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

def verificar_usuario(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username=username).exists() or Colaborador.objects.filter(username=username).exists()
    }
    return JsonResponse(data)



def eliminar_colaborador_aprobado(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    colaborador.delete()
    sweetify.success(request, 'Colaborador eliminado con éxito.')
    return redirect('listar_colaboradores_aprobados')



def iniciarsesionColaborador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
           
            colaborador = Colaborador.objects.get(username=username, estado='aprobado')
            print(colaborador)
            if colaborador.check_password(password):
            
                request.session['colaborador_id'] = colaborador.id
                print(request.session['colaborador_id'])
                sweetify.success(request, 'Inicio de sesión exitoso.')
                return redirect('inicio_colaborador')
            else:
                sweetify.error(request, 'Contraseña incorrecta.')
                return redirect('iniciarsesionColaborador')
        except Colaborador.DoesNotExist:
           
            sweetify.error(request, 'Colaborador no registrado. Regístrate para continuar.')
            return redirect('iniciarsesionColaborador')

    return render(request, 'base/colaborador/iniciarsesionColaborador.html')

@colaborador_required
def cerrar_sesion_colaborador(request):
    if 'colaborador_id' in request.session:
        request.session.flush()

    sweetify.success(request, 'Sesión cerrada exitosamente.')
    return redirect('colaborador')

@colaborador_required
def inicio_colaborador(request):
    colaborador_id = request.session.get('colaborador_id')
    
    if not colaborador_id:
        return redirect('colaborador')

    colaborador = Colaborador.objects.get(id=colaborador_id)
    
    contexto = {
        'colaborador': colaborador,
    }
    return render(request, 'base/colaborador/inicio_colaborador.html', contexto)

@colaborador_required
def eliminar_reserva(request, reserva_id):
    colaborador_id = request.session.get('colaborador_id')
    print(colaborador_id)
    if not colaborador_id:
        # Si no hay colaborador_id en la sesión, redirigir a la página de inicio de sesión de colaboradores
        return redirect('iniciarsesionColaborador')

    # Verificar si el colaborador existe
    try:
        colaborador = Colaborador.objects.get(id=colaborador_id)
    except Colaborador.DoesNotExist:
        # Si no encuentra un colaborador, redirigir a otra página, como la página de error o principal
        sweetify.error(request, 'Colaborador no encontrado.')
        return redirect('horas_disponibles')  # Redirige a una página de error o donde consideres adecuado

    # Obtener la reserva de disponibilidad
    reserva = get_object_or_404(Disponibilidad, id=reserva_id, colaborador_id=colaborador_id)

    # Verificar si existe una reserva de servicio que coincida con la hora y la fecha de la disponibilidad
    existe_reserva_servicio = ReservaServicio.objects.filter(
        colaborador_id=colaborador_id,
        fecha_reservada=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin
    ).exists()

    if existe_reserva_servicio:
        # Si ya existe una reserva de servicio para esa hora, mostrar error
        sweetify.error(request, 'No puedes eliminar esta disponibilidad porque ya existe una reserva para esta hora.')
        return redirect('horas_disponibles')

    # Si no existe ninguna reserva de servicio, eliminar la disponibilidad
    reserva.delete()
    sweetify.success(request, 'Disponibilidad eliminada con éxito.')
    
    return redirect('horas_disponibles')