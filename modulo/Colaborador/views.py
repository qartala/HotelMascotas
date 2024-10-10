from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from modulo.Colaborador.models import Colaborador
import re
import sweetify
from .forms import DisponibilidadForm, PerfilColaboradorForm
from .models import Disponibilidad

# Create your views here.

def colaborador(request):
    return render(request,'base/colaborador/colaborador.html')

def listar_colaboradores(request):
    colaborador = Colaborador.objects.all()
    contexto = {
        'colaborador': colaborador
    }
    return render(request, 'base/solicitudes.html', context=contexto)

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
            disponibilidad.servicio = colaborador.servicio  

            conflicto = Disponibilidad.objects.filter(
                colaborador=colaborador,
                servicio=disponibilidad.servicio,
                fecha=disponibilidad.fecha,
                hora_inicio=disponibilidad.hora_inicio
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

def perfil_colaborador(request):
    colaborador_id = request.session.get('colaborador_id')

    if not colaborador_id: 
        return redirect('iniciarsesionColaborador')

    colaborador = Colaborador.objects.get(id=colaborador_id)

    if request.method == 'POST':
        form = PerfilColaboradorForm(request.POST, request.FILES, instance=colaborador)
        if form.is_valid():
            form.save()
            return redirect('perfil_colaborador')  
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
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        servicio = request.POST.get('service')
        pdf_file = request.FILES.get('pdf_file')

        if len(fullname) > 100:
            messages.error(request, 'El nombre completo no puede tener más de 100 caracteres.')
            return render(request, 'base/colaborador/colaborador.html')

        if len(username) > 15:
            messages.error(request, 'El nombre de usuario no puede tener más de 15 caracteres.')
            return render(request, 'base/colaborador/colaborador.html')

        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[.-]).{1,15}$', username):
            messages.error(request, 'El nombre de usuario debe contener al menos una mayúscula, un número y un punto o guion.')
            return render(request, 'base/colaborador/colaborador.html')

        if Colaborador.objects.filter(username=username).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya está en uso.")
            return render(request, 'base/colaborador/colaborador.html')

        if not re.match(r'^\+569\d{8}$', phone):
            messages.error(request, 'El número de teléfono debe tener el formato +56 9 y luego 8 dígitos.')
            return render(request, 'base/colaborador/colaborador.html')

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            messages.error(request, 'Introduce una dirección de correo válida.')
            return render(request, 'base/colaborador/colaborador.html')

        if Colaborador.objects.filter(email=email).exists():
            messages.error(request, f"El correo electrónico '{email}' ya está en uso.")
            return render(request, 'base/colaborador/colaborador.html')

        if len(password) > 15:
            messages.error(request, 'La contraseña no puede tener más de 15 caracteres.')
            return render(request, 'base/colaborador/colaborador.html')

        if not re.match(r'^(?=.*[A-Z]).{1,15}$', password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
            return render(request, 'base/colaborador/colaborador.html')

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
        messages.success(request, 'Registro exitoso. Espera la confirmación del administrador.')
        return redirect('registro_colaborador')

    return render(request, 'base/colaborador/colaborador.html')

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
    
    messages.success(request, 'Colaborador eliminado con éxito.')
    
    return redirect('listar_colaboradores_aprobados')

def listar_colaboradores_aprobados(request):
    colaboradores_aprobados = Colaborador.objects.filter(estado='aprobado')
    return render(request, 'base/admin/colaboradores_aprobados.html', {'colaboradores': colaboradores_aprobados})

def iniciarsesionColaborador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
           
            colaborador = Colaborador.objects.get(username=username, estado='aprobado')
            if colaborador.check_password(password):
            
                request.session['colaborador_id'] = colaborador.id
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('inicio_colaborador')  
            else:
                messages.error(request, 'Contraseña incorrecta.')
                return redirect('iniciarsesionColaborador')
        except Colaborador.DoesNotExist:
           
            messages.error(request, 'Colaborador no registrado. Regístrate para continuar.')
            return redirect('registro_colaborador')  

    return render(request, 'base/colaborador/iniciarsesionColaborador.html')
 
def inicio_colaborador(request):
    colaborador_id = request.session.get('colaborador_id')
    
    if not colaborador_id:
        return redirect('colaborador')

    colaborador = Colaborador.objects.get(id=colaborador_id)
    
    contexto = {
        'colaborador': colaborador,
    }
    return render(request, 'base/colaborador/inicio_colaborador.html', contexto)

def eliminar_reserva(request, reserva_id):
    colaborador_id = request.session.get('colaborador_id')
    if not colaborador_id:
        return redirect('iniciarsesionColaborador')
    reserva = get_object_or_404(Disponibilidad, id=reserva_id, colaborador_id=colaborador_id)
    reserva.delete()

    return redirect('horas_disponibles')    