from logging import error
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from modulo.Usuario.models import  Usuario ,Suscripcion
from .models import User
from modulo.Producto.models import Habitacion
import datetime
import sweetify
from django.contrib import messages

# Create your views here.
def admin(request):
    return render(request,'base/administrador.html')

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
        contrasenia = request.POST['contrasenia']
        correo = request.POST['correo']
        try:
            usuario_creado, se_creo = User.objects.get_or_create(
                                        username = usuario,
                                        password = contrasenia,
                                        email = correo
                                        )          #el usuario es unico, por si lo duplico dara error
        except Exception as ex:
            codigo_error =int (ex.args[0])
            if codigo_error == 1062:
                
             sweetify.warning(request, 'Usuario ya existe, no se creo :C') 
    
            return render(request,'base/Registrarse.html')

    contexto = {}
    if se_creo:
        usuario_creado.set_password(contrasenia)
        usuario_creado.save()
        nuevoUsuario = Usuario()
        nuevoUsuario.idUsuario = usuario_creado
        nuevoUsuario.tipo_cuenta = 'Usuario'
        nuevoUsuario.save()
        return HttpResponseRedirect(reverse('iniciarsesion'))
        
    else:
        sweetify.warning(request, 'Usuario ya existe, no se creo :C') 
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
            messages.success(request, 'Inicio de sesión exitoso')
            return redirect('principalUsuario')
        else:
            sweetify.warning(request, 'Usuario y contraseña no existen :C')
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
# hay que agregar esto a las urls 



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
