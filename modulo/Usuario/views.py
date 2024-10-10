from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from modulo.Producto.models import Habitacion, Reserva
from modulo.Colaborador.models import Colaborador
from modulo.Usuario.models import Usuario
from modulo.Producto.models import Membresia
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

def perfil (request):
        tipo = request.user
        print(tipo)
        return render(request, 'base/usuario/perfil.html')

def listar_reservas_view(request):
    print(request.user)
    reservas = Reserva.objects.filter(cliente=request.user)
    print(reservas)
    return render(request, 'base/usuario/listar_reservas.html', {'reservas': reservas})
    
def ficha_salud_view(request):
    if request.method == 'POST':
        form = FichaSaludForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False) 
            usuario = Usuario.objects.get(idUsuario=request.user)  
            form.id_usuario = usuario  
            form.save()
            return render(request,'base/perfil.html')  
    else:
        form = FichaSaludForm()
    return render(request, 'base/usuario/ficha.html', {'form': form})

def listar_fichas_view(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    fichas = Ficha.objects.filter(id_usuario=usuario)
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
    ficha.delete()
    return redirect('perfil')  

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

def cerrar_sesion(request):
    if request.user.is_authenticated:
        logout(request)

    storage = messages.get_messages(request)
    for message in storage:
        message.used = True  

    return HttpResponseRedirect(reverse('principal'))

def reservas_hotel(request):
        return render(request,'base/usuario/reservas_hotel.html')