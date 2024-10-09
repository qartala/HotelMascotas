from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from logging import error
from modulo.Producto.models import Habitacion, Reserva
from modulo.Usuario.models import Usuario, Suscripcion, Colaborador, Membresia
import re
import sweetify
from .forms import DisponibilidadForm, FichaSaludForm, PerfilColaboradorForm
from .models import Disponibilidad, Ficha



def principal(request):
    buscar = request.GET.get("buscar", "")
    productos = Habitacion.objects.filter(numero_habitacion__icontains=buscar)
    contexto = {
        'productos': productos
    }
    return render(request, 'base/usuario/caso.html', context=contexto)

def perfil (request):
        tipo = request.user
        print(tipo)
        return render(request, 'base/perfil.html')

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
    return render(request, 'base/ficha.html', {'form': form})

def listar_fichas_view(request):
    usuario = Usuario.objects.get(idUsuario=request.user)
    fichas = Ficha.objects.filter(id_usuario=usuario)
    return render(request, 'base/listar_fichas.html', {'fichas': fichas})

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
    return render(request, 'base/editar_ficha.html', {'form': form})

def eliminar_ficha(request, id):
    ficha = get_object_or_404(Ficha, id=id)
    ficha.delete()
    return redirect('perfil')  

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

def eliminar_reserva(request, reserva_id):
    colaborador_id = request.session.get('colaborador_id')
    if not colaborador_id:
        return redirect('iniciarsesionColaborador')
    reserva = get_object_or_404(Disponibilidad, id=reserva_id, colaborador_id=colaborador_id)
    reserva.delete()

    return redirect('horas_disponibles')

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

def solicitudes_admin(request):
    storage = messages.get_messages(request)
    for message in storage:
        if "Inicio de sesión exitoso" in message.message:
            message.used = True  

    solicitudes = Colaborador.objects.filter(estado='pendiente')
    
    return render(request, 'base/admin/solicitudes.html', {'solicitudes': solicitudes})


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

    storage = messages.get_messages(request)
    for message in storage:
        message.used = True  

    return HttpResponseRedirect(reverse('principal'))

def principalUsuario (request):
    
    suscrito = Suscripcion.objects.all()
    productos = Habitacion.objects.all()
    membresias = Membresia.objects.all()
    usuario = Usuario.objects.get(idUsuario=request.user)
    mascotas = Ficha.objects.filter(id_usuario=usuario)

    contexto = {
        'productos':productos,
        'suscrito':suscrito,
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

def crear_membresia(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descuento = request.POST['descuento']
        duracion = request.POST['duracion_dias']
        valor = request.POST['valor']  # Captura el valor de la membresía desde el formulario

        # Crear y guardar la membresía con el nuevo campo valor
        nueva_membresia = Membresia(
            nombre=nombre, 
            descuento=descuento, 
            duracion_dias=duracion, 
            valor=valor  # Guarda el valor
        )
        nueva_membresia.save()

        sweetify.success(request, 'Membresía creada exitosamente.')
        return redirect('crear_membresia')

    return render(request, 'base/admin/crearMembresia.html')

def gestionar_membresias(request):
    membresias = Membresia.objects.all()  # Obtener todas las membresías

    if request.method == 'POST':
        membresia_id = request.POST.get('membresia_id')
        accion = request.POST.get('accion')

    return render(request, 'base/admin/gestionMembresia.html', {'membresias': membresias})

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

        messages.success(request, 'Membresía actualizada con éxito.')
        return redirect('gestionar_membresias')

    return render(request, 'base/admin/editarMembresia.html', {'membresia': membresia})

def eliminar_membresia(request, membresia_id):
    membresia = get_object_or_404(Membresia, id=membresia_id)
    membresia.delete()
    messages.success(request, 'Membresía eliminada con éxito.')
    return redirect('gestionar_membresias')