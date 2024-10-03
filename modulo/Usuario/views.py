from logging import error
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from modulo.Usuario.models import Usuario, Suscripcion, Colaborador
from django.core.mail import send_mail
from modulo.Producto.models import Habitacion
import datetime
from django.db import IntegrityError
import sweetify
import re
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Ficha
from .forms import FichaSaludForm
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.template.loader import render_to_string


def admin(request):
    return render(request,'base/administrador.html')

def principal(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(tipoPerro__icontains=buscar)
    contexto = {
        'productos': productos
    }
    return render(request, 'base/caso.html', context=contexto)

def perfil (request):
        tipo = request.user
        print(tipo)
        return render(request, 'base/perfil.html')
def ficha_salud_view(request):
    if request.method == 'POST':
        form = FichaSaludForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False) # No guarda el objeto aún
            usuario = Usuario.objects.get(idUsuario=request.user)  
            form.id_usuario = usuario  # Asigna el usuario autenticado
            form.save()
            return render(request,'base/perfil.html')  # Redirige a la lista de fichas tras guardar
    else:
        form = FichaSaludForm()
    return render(request, 'base/ficha.html', {'form': form})

def listar_fichas_view(request):
    # Obtener el usuario autenticado
    usuario = Usuario.objects.get(idUsuario=request.user)
    # Filtrar las fichas por el usuario autenticado
    fichas = Ficha.objects.filter(id_usuario=usuario)
    return render(request, 'base/listar_fichas.html', {'fichas': fichas})

def editar_ficha_view(request, pk):
    ficha = get_object_or_404(Ficha, pk=pk)  # Obtiene la ficha por su ID
    if request.method == 'POST':
        form = FichaSaludForm(request.POST, instance=ficha)  # Carga la instancia de la ficha
        if form.is_valid():
            form.save()  # Guarda los cambios
            return redirect('listar_fichas')  # Redirige a la lista de fichas
    else:
        form = FichaSaludForm(instance=ficha)  # Carga la instancia para el formulario

    return render(request, 'base/editar_ficha.html', {'form': form})

def eliminar_ficha(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    ficha.delete()
    return redirect('perfil')  # Redirige a la lista de fichas tras eliminar

def colaborador(request):
    return render(request,'base/colaborador.html')

def listar_colaboradores(request):
    colaborador = Colaborador.objects.all()
    contexto = {
        'colaborador': colaborador
    }
    return render(request, 'base/solicitudes.html', context=contexto)

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
            return render(request, 'base/colaborador.html')

        if len(username) > 15:
            messages.error(request, 'El nombre de usuario no puede tener más de 15 caracteres.')
            return render(request, 'base/colaborador.html')
        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[.-]).{1,15}$', username):
            messages.error(request, 'El nombre de usuario debe contener al menos una mayúscula, un número y un punto o guion.')
            return render(request, 'base/colaborador.html')

        if User.objects.filter(username=username).exists() or Colaborador.objects.filter(username=username).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya está en uso.")
            return render(request, 'base/colaborador.html')

        if not re.match(r'^\+569\d{8}$', phone):
            messages.error(request, 'El número de teléfono debe tener el formato +56 9 y luego 8 dígitos.')
            return render(request, 'base/colaborador.html')

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            messages.error(request, 'Introduce una dirección de correo válida.')
            return render(request, 'base/colaborador.html')

        if User.objects.filter(email=email).exists() or Colaborador.objects.filter(email=email).exists():
            messages.error(request, f"El correo electrónico '{email}' ya está en uso.")
            return render(request, 'base/colaborador.html')

        if len(password) > 15:
            messages.error(request, 'La contraseña no puede tener más de 15 caracteres.')
            return render(request, 'base/colaborador.html')
        if not re.match(r'^(?=.*[A-Z]).{1,15}$', password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
            return render(request, 'base/colaborador.html')

        colaborador = Colaborador(
            fullname=fullname,
            username=username,
            phone=phone,
            email=email,
            servicio=servicio,
            pdf_file=pdf_file
        )
        colaborador.save()

        messages.success(request, 'Registro exitoso. Espera la confirmación del administrador.')
        return redirect('registro_colaborador')

    return render(request, 'base/colaborador.html')

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

def solicitudes_admin(request):
    storage = messages.get_messages(request)
    for message in storage:
        if "Inicio de sesión exitoso" in message.message:
            message.used = True  

    solicitudes = Colaborador.objects.filter(estado='pendiente')
    
    return render(request, 'base/solicitudes.html', {'solicitudes': solicitudes})


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

def eliminar_colaborador_aprobado(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, id=colaborador_id)
    
    colaborador.delete()
    
    messages.success(request, 'Colaborador eliminado con éxito.')
    
    return redirect('listar_colaboradores_aprobados')


def listar_colaboradores_aprobados(request):
    colaboradores_aprobados = Colaborador.objects.filter(estado='aprobado')
    return render(request, 'base/colaboradores_aprobados.html', {'colaboradores': colaboradores_aprobados})


def iniciarsesionColaborador(request):
    return render(request,'base/iniciarsesionColaborador.html')

def listar(request):
    usuarios = User.objects.all()

    contexto = {
        'usuarios':usuarios
    }
    return render(request,'base/listarUsuario.html', context = contexto)


def suscripcion(request):
     
    usuario = Usuario.objects.get(idUsuario = request.user.id)
    
    contexto= {
        'usuario' :usuario
        }
    
    if request.method == 'GET':
        return render(request,'base/suscribirse.html',contexto) 
 
    elif request.method == 'POST':
        contexto = {}
        
        nuevoSuscriptor = usuario
        nuevoSuscriptor.id
        nuevoS= Suscripcion()
        nuevoS.f_suscripcion = datetime.datetime.now()
        nuevoS.monto = request.POST['monto']
        nuevoS.id_usuario =  Usuario.objects.get(id = nuevoSuscriptor.id)
        if  int( nuevoS.monto )>= 5000:
            if int ( nuevoS.monto )>= 100000:
                sweetify.warning(request,'El monto es muy alto')
            else:
                nuevoS.save()
                return HttpResponseRedirect(reverse('principalUsuario'))
            
        else:
            sweetify.warning(request, 'El monto debe ser igual ó mayor a 5000')
            return render(request,'base/suscribirse.html',contexto) 
    return render(request,'base/suscribirse.html',contexto)


def desuscribirse(request):
    if request.method == 'GET':
        return render(request,'base/DeSuscribirse.html')
    
    elif request.method == 'POST':
        cliente = Usuario.objects.get(idUsuario = request.user.id)
        Suscrito = Suscripcion.objects.filter(id_usuario = cliente.id)
        Suscrito.delete()
        return HttpResponseRedirect(reverse('principalUsuario'))
    
        
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
                sweetify.warning(request, 'Usuario ya existe, no se creó :C')
                return render(request, 'base/Registrarse.html')

            usuario_creado.set_password(contrasenia)
            usuario_creado.save()

            nuevoUsuario = Usuario()
            nuevoUsuario.idUsuario = usuario_creado
            nuevoUsuario.tipo_cuenta = 'Usuario'
            nuevoUsuario.save()

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
                return redirect('vistaAdmin')  
            else:
                return redirect('principalUsuario')  
        else:
            messages.error(request, 'Usuario y contraseña no existen :C')
            return render(request, 'base/IniciarSesion.html')



def eliminarSuscriptor(request):
    if request.method == 'GET':
        return render(request,'base/listarUsuario.html')

    elif request.method == 'POST':
        contexto = {}
        usuario = request.POST['User']

        try:
            usuario_econtrado = User.objects.get(username = usuario )

        except User.DoesNotExist:
            contexto['mensaje'] = "Usuario no encontrado"
            return render(request,'base/listarUsuario.html',contexto)

        if request.method == 'POST':
            usuario_econtrado.f_termino = datetime.datetime.now()
    return render(request,'base/ingresar.s.html')

def ingresarSuscriptor(request):
    if request.method == 'GET':
        return render(request,'base/ingresar.s.html') 

    elif request.method == 'POST':
        contexto = {}
        usuario = request.POST['User']
        
        try:
            usuario_econtrado = User.objects.get(username = usuario )
            usuario_econtrado.id
            usuario2 = Usuario.objects.get(idUsuario_id = usuario_econtrado.id)
            nuevoS= Suscripcion()
            nuevoS.f_suscripcion = datetime.datetime.now()
            nuevoS.monto = 0
            nuevoS.id_usuario =  Usuario.objects.get(id  = usuario2.id  )
            nuevoS.save()
            sweetify.success(request, 'Usuario ingresado con éxito!!!') 
            return render(request,'base/ingresar.s.html') 
           
        except User.DoesNotExist:
            sweetify.warning(request, 'Usuario no encontrado')  
            return render(request,'base/ingresar.s.html',contexto) 
    return render(request,'base/ingresar.s.html') 

def vigencia (request):
    vigentes  = Suscripcion.objects.all()
    contexto = { 
        'vigentes':vigentes
    }
   
    return render(request,'base/Vigencia.html',contexto)

def eliminar_suscriptor(request,id_s):
    suscriptor = Suscripcion.objects.get( id = id_s)
    suscriptor.delete()
    sweetify.success(request, 'Suscriptor Eliminado con éxito!!!') 
    return HttpResponseRedirect(reverse('vigencia'))

def cerrar_sesion(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('principal')) 


def principalUsuario (request):
    
    suscrito = Suscripcion.objects.all()
    productos = Habitacion.objects.all()

    contexto = {
        'productos':productos,
        'suscrito':suscrito,
    }
    
    contexto = {}
    buscar = ""
    try:
        buscar = request.GET["buscar"]
    except Exception:
        pass
    if request.method == "GET":
        
        productos = Habitacion.objects.filter(tipoPerro__contains=buscar)
        contexto["productos"] = productos
    return render(request,'base/casoUsuario.html',context = contexto)
