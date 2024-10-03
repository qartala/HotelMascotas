from logging import error
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from modulo.Usuario.models import  Usuario ,Suscripcion
from .models import User
from modulo.Producto.models import Habitacion
import datetime
import sweetify
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Ficha
from .forms import FichaSaludForm
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.template.loader import render_to_string

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

def colaborador(request):
    return render(request,'base/colaborador.html')


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
        return render(request,'base/Registrarse.html')
        
    elif request.method =='POST':
        usuario = request.POST['usuario']
        nombre = request.POST['nombre']
        contrasenia = request.POST['contrasenia']
        correo = request.POST['correo']
        try:
            usuario_creado, se_creo = User.objects.get_or_create(
                                        username = usuario,
                                        first_name = nombre,
                                        password = contrasenia,
                                        email = correo
                                        )          #el usuario es unico, por si lo duplico dara error
        except Exception as ex:
            codigo_error =int (ex.args[0])
            if codigo_error == 1062:
                
             sweetify.warning(request, 'El nombre de usuario ya existe') 
    
            return render(request,'base/Registrarse.html')

    contexto = {}
    if se_creo:
        usuario_creado.set_password(contrasenia)
        usuario_creado.save()
        nuevoUsuario = Usuario()
        nuevoUsuario.idUsuario = usuario_creado
        nuevoUsuario.save()
        return HttpResponseRedirect(reverse('iniciarsesion'))
        
    else:
        sweetify.warning(request, 'El nombre de usuario ya existe')
    return render(request,'base/Registrarse.html',contexto)

def iniciarsesion(request):
    if request.method == 'GET':
        return render(request, 'base/IniciarSesion.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')
        usuario_encontrado = authenticate(username=usuario, password=contrasenia)
        if usuario_encontrado is not None:
            login(request, usuario_encontrado)
            sweetify.success(request, 'Inicio de sesión exitoso', button='Continuar')
            
            if usuario_encontrado.is_superuser:
                return redirect('vistaAdmin')  # Redirige al panel de admin
            else:
                return redirect('principalUsuario')  # Redirige al sitio normal
        else:
            messages.error(request, 'El usuario no existe')
            return render(request, 'base/IniciarSesion.html')  # Muestra el formulario de nuevo

    # Si la solicitud no es GET ni POST, redirige o maneja el error de otra manera.



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
# hay que agregar esto a las urls 



def cerrar_sesion(request):
    print(f"Usuario autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        print("Cerrando sesión del usuario")
        logout(request)
        request.session.flush()
    return redirect('iniciarsesion')


def principalUsuario (request):
    if request:
        suscrito = Suscripcion.objects.all()
        productos = Habitacion.objects.all()

        contexto = {
            'productos':productos,
            'suscrito':suscrito,
        }
        
        
        buscar = request.GET.get("buscar", "")
        if request.method == "GET" and buscar:
            productos = Habitacion.objects.filter(tipoPerro__contains=buscar)
            contexto["productos"] = productos
        return render(request,'base/casoUsuario.html',context = contexto)
