from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from modulo.Colaborador.models import Colaborador, Disponibilidad
import re
import sweetify
from django.core.exceptions import ValidationError
from .forms import DisponibilidadForm, PerfilColaboradorForm
from .models import Disponibilidad
from .decorators import colaborador_required

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
    
    reservas = Disponibilidad.objects.filter(colaborador=colaborador, fecha__range=[hoy, en_30_dias])
    
    contexto = {
        'reservas': reservas,
        'colaborador': colaborador,  
    }
    
    return render(request, 'base/colaborador/horas_disponibles.html', contexto)


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
                    form.add_error(None, "Ya has registrado una disponibilidad para este servicio en este horario.")
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
    if not colaborador_id:
        return redirect('iniciarsesionColaborador')
    reserva = get_object_or_404(Disponibilidad, id=reserva_id, colaborador_id=colaborador_id)
    reserva.delete()

    return redirect('horas_disponibles')