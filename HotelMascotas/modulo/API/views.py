# views.py
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.views import APIView
from modulo.Producto.models import  Reserva, Habitacion, Regalia,Membresia, ReservaRegalia,Video
from django.contrib.auth.models import User
from datetime import timedelta
from modulo.Producto.models import Video, Reserva
from modulo.Usuario.models import Ficha, Usuario
from rest_framework.parsers import MultiPartParser, FormParser
from modulo.Usuario.models import Usuario, Ficha ,ServiciosComunes,Mensaje
import json
from .serializers import (
    ReservaSerializer,
    UserSerializer,
    FichaSerializer,
    HabitacionSerializer,
    RegaliaSerializer,
    ServiciosComunesSerializer,
    MensajeSerializer,
    MembresiaSerializer,
    ReservaRegaliaSerializer,
    VideoListSerializer,
    VideoUploadSerializer
)
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class EstadoMembresiaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user.usuario  # Usuario autenticado
        tiene_membresia_activa = usuario.tiene_membresia_activa()
        return Response({
            'tiene_membresia_activa': tiene_membresia_activa,
            'fecha_inicio': usuario.fecha_inicio_membresia,
            'membresia_duracion': usuario.membresia.duracion_dias if usuario.membresia else None,
        })
        
class ListarTodasReservasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Verificar que el usuario es un trabajador
        usuario = request.user.usuario
        if not usuario.trabajador:
            return Response(
                {"error": "No tienes permisos para acceder a esta información."},
                status=403,
            )

        # Obtener todas las reservas
        reservas = Reserva.objects.all().select_related("cliente", "habitacion", "mascota")
        serializer = ReservaSerializer(reservas, many=True, context={"request": request})
        return Response(serializer.data, status=200)


class ListarVideosReservaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reserva_id):
        usuario = request.user.usuario  # Usuario autenticado
        
        if usuario.trabajador:  # Si es un trabajador, no filtrar por cliente
            videos = Video.objects.filter(reserva_id=reserva_id)
        else:  # Si es un cliente, filtrar por cliente autenticado
            videos = Video.objects.filter(reserva_id=reserva_id, cliente=usuario)
        
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)



class EliminarVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, cliente=request.user.usuario)
            video.delete()
            return Response({"message": "Video eliminado correctamente."}, status=200)
        except Video.DoesNotExist:
            return Response({"error": "El video no existe o no tienes permisos para eliminarlo."}, status=404)
        

from rest_framework.parsers import MultiPartParser, FormParser

class SubirVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Permitir subida de archivos

    def post(self, request):
        usuario = request.user.usuario  # Usuario autenticado
        print(f"Verificando membresía para el usuario: {usuario}")
        print(f"Membresía activa: {usuario.tiene_membresia_activa()}")

        # Verificar si el usuario tiene una membresía activa
        if not usuario.tiene_membresia_activa():
            return Response({"error": "Debes tener una membresía activa para subir videos."}, status=403)

        # Validar los datos usando el serializer
        serializer = VideoUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Guardar el video
            video = serializer.save()
            return Response(
                {
                    "message": "Video subido exitosamente.",
                    "video_id": video.id,
                    "descripcion": video.descripcion,
                    "fecha_subida": video.fecha_subida,
                },
                status=201,
            )
        else:
            print(f"Errores del serializer: {serializer.errors}")
            return Response(serializer.errors, status=400)


# Listar y crear servicios
class ServiciosComunesListCreateView(generics.ListCreateAPIView):
    queryset = ServiciosComunes.objects.all()
    serializer_class = ServiciosComunesSerializer

# Obtener, actualizar o eliminar un servicio específico
class ServiciosComunesDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiciosComunes.objects.all()
    serializer_class = ServiciosComunesSerializer

# Reserva
class ReservaList(generics.ListCreateAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    # Campos para filtrar
    filterset_fields = {
        'cliente__id': ['exact'],  # Filtrar por ID del cliente
        'cliente__username': ['exact', 'icontains'],  # Filtrar por nombre de usuario
        'habitacion__id': ['exact'],  # Filtrar por ID de la habitación
        'habitacion__numero_habitacion': ['exact', 'icontains'],  # Filtrar por número de habitación
        'fecha_inicio': ['gte', 'lte'],  # Rango de fechas de inicio
        'fecha_fin': ['gte', 'lte'],  # Rango de fechas de fin
        'pagado': ['exact'],  # Filtrar por estado de pago
        'cancelada': ['exact'],  # Filtrar por reservas canceladas
        'check_in': ['exact'],  # Filtrar por estado de check-in
    }
    
    # Campos para búsqueda
    search_fields = [
        'cliente__username', 
        'habitacion__numero_habitacion', 
        'mascota__nombre_perro'
    ]

class ReservaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

# Usuario
class UsuarioList(generics.ListCreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer

class UsuarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer

# Ficha
class FichaList(generics.ListCreateAPIView):
    queryset = Ficha.objects.all()
    serializer_class = FichaSerializer

class FichaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ficha.objects.all()
    serializer_class = FichaSerializer

# Habitacion
class HabitacionList(generics.ListCreateAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

class HabitacionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

# Regalia
class RegaliaList(generics.ListCreateAPIView):
    queryset = Regalia.objects.all()
    serializer_class = RegaliaSerializer

class RegaliaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Regalia.objects.all()
    serializer_class = RegaliaSerializer


# Membresia
class MembresiaList(generics.ListCreateAPIView):
    queryset = Membresia.objects.all()
    serializer_class = MembresiaSerializer

class MembresiaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Membresia.objects.all()
    serializer_class = MembresiaSerializer

#reserva-regalia 

class ReservaRegaliaList(generics.ListCreateAPIView):
    queryset = ReservaRegalia.objects.all()
    serializer_class = ReservaRegaliaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    filterset_fields = {
        'cliente__id': ['exact'],  # Filtrar por ID del cliente
        'cliente__username': ['exact', 'icontains'],  # Filtrar por nombre de usuario
        'regalia__id': ['exact'],  # Filtrar por ID de la regalia
        'regalia__nombre': ['exact', 'icontains'],  # Filtrar por nombre de la regalia
        'fecha': ['gte', 'lte'],  # Rango de fechas
        'precio_total_r': ['gte', 'lte'],  # Rango de precios totales
        'reserva__id': ['exact'],  # Filtrar por ID de la reserva
        'reserva__habitacion__numero_habitacion': ['exact', 'icontains'],  # Filtrar por número de habitación
    }
    
    # Campos para búsqueda
    search_fields = [
        'cliente__username', 
        'regalia__nombre', 
        'reserva__habitacion__numero_habitacion',  # Permitir búsqueda por número de habitación
    ]

class ReservaRegaliaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReservaRegalia.objects.all()
    serializer_class = ReservaRegaliaSerializer



@csrf_exempt  # Desactiva la verificación CSRF para solicitudes API
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            username = data.get('username')
            password = data.get('password')

            # Verificar si el usuario existe en la base de datos
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Autenticar al usuario con la contraseña
            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                # Obtener el modelo Usuario relacionado
                usuario = Usuario.objects.get(idUsuario=user)

                # Verificar si el usuario es trabajador
                if usuario.trabajador:
                    # Asignar el trabajador a las reservas pendientes sin trabajador asignado
                    reservas_actualizadas = Reserva.objects.filter(trabajador__isnull=True).update(trabajador=user)
                    print(f"Se han asignado {reservas_actualizadas} reservas al trabajador {user.username}")

                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)

                # Crear un diccionario con los datos relevantes del usuario
                usuario_data = {
                    'id': usuario.idUsuario.id,
                    'username': usuario.idUsuario.username,
                    'tipo_cuenta': usuario.tipo_cuenta,
                    'membresia': usuario.membresia.nombre if usuario.membresia else None,
                    'telefono': usuario.telefono,
                    'direccion': usuario.direccion,
                    'fecha_nacimiento': usuario.fecha_nacimiento,
                    'trabajador': usuario.trabajador,
                    'fecha_inicio_membresia': usuario.fecha_inicio_membresia,
                }

                # Devolver la respuesta con los tokens y los datos del usuario
                return JsonResponse({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'usuario': usuario_data  # Enviar el modelo de usuario al frontend
                }, status=200)
            else:
                return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)

        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ficha_mascota(request, reserva_id):
    try:
        # Verificar que la reserva esté asignada al trabajador autenticado
        reserva = Reserva.objects.get(id=reserva_id, trabajador=request.user)
        
        # Obtener la ficha de la mascota asociada a la reserva
        ficha = Ficha.objects.get(id_usuario=reserva.mascota.id_usuario)
        serializer = FichaSerializer(ficha)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Reserva.DoesNotExist:
        return Response({"error": "No tienes acceso a esta reserva"}, status=status.HTTP_403_FORBIDDEN)

    except Ficha.DoesNotExist:
        return Response({"error": "Ficha no encontrada"}, status=status.HTTP_404_NOT_FOUND)


@require_http_methods(["POST"])
def check_in_view(request, reserva_id):
    # Obtener la reserva o devolver un error 404 si no existe
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.check_in:
        return JsonResponse(
            {'message': 'El check-in ya ha sido realizado.'}, 
            status=400  
        )

    # Marcar la reserva como check-in realizada
    reserva.check_in = True
    reserva.save()

    return JsonResponse(
        {'message': 'Check-in realizado con éxito.', 'reserva_id': reserva.id}, 
        status=200  
    )

@api_view(['PUT'])
def actualizar_check_in(request, id):
    try:
        # Obtener la reserva por ID
        reserva = Reserva.objects.get(pk=id)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    # Solo permitir la actualización del campo check_in
    data = request.data.get('check_in')

    if data is not None:
        reserva.check_in = data  
        reserva.save()  
        return Response({'mensaje': 'Check-in actualizado correctamente'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Campo check_in requerido'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
def actualizar_pagado(request, id):
    try:
        # Obtener la reserva por ID
        reserva = Reserva.objects.get(pk=id)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    # Obtener el campo pagado de la solicitud
    pagado = request.data.get('pagado')

    if pagado is not None:
        reserva.pagado = pagado  
        reserva.save()  
        return Response({
            'mensaje': 'Estado de pago actualizado correctamente',
            'pagado': reserva.pagado
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Campo pagado requerido'}, status=status.HTTP_400_BAD_REQUEST)

class ServiciosComunesView(APIView):
    def get(self, request, id_ficha, id_reserva):
        # Obtener la ficha y la reserva asociada
        ficha = get_object_or_404(Ficha, id=id_ficha)
        reserva = get_object_or_404(Reserva, id=id_reserva, mascota=ficha)

        # Crear servicios comunes para cada día de la reserva si no existen
        servicios_por_dia = []
        fecha_inicio = reserva.fecha_inicio
        fecha_fin = reserva.fecha_fin
        dias_reserva = (fecha_fin - fecha_inicio).days + 1

        for i in range(dias_reserva):
            dia_numero = i + 1
            fecha_actual = fecha_inicio + timedelta(days=i)

            # Verificar si ya existe un servicio para este día específico
            servicio, created = ServiciosComunes.objects.get_or_create(
                ficha=ficha,
                reserva=reserva,
                dia=dia_numero,
                defaults={
                    'comio': False,
                    'paseo': False,
                    'entretencion': False,
                    'medicamentos': False,
                    'fecha_registro': fecha_actual
                }
            )
            servicios_por_dia.append(servicio)

        # Serializar y devolver todos los servicios comunes para la ficha y reserva específicos
        serializer = ServiciosComunesSerializer(servicios_por_dia, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SubirEvidenciaView(APIView):
    def post(self, request, pk, campo):
        servicio = get_object_or_404(ServiciosComunes, pk=pk)
        
        if campo in ['comio_evidencia', 'regalo_evidencia', 'paseo_evidencia', 'entretencion_evidencia', 'medicamentos_evidencia']:
            file = request.FILES.get('file')
            if file:
                setattr(servicio, campo, file)
                servicio.save()
                return Response({'status': 'Evidencia subida con éxito'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No se proporcionó un archivo'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Campo no válido'}, status=status.HTTP_400_BAD_REQUEST)
    
from .serializers import UsuarioSerializer

@api_view(['GET'])
def perfil_view(request):
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(idUsuario=request.user)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
@api_view(['GET'])
def historial_chat(request, reserva_id):
    try:
        mensajes = Mensaje.objects.filter(reserva_id=reserva_id).order_by('fecha_hora')
        serializer = MensajeSerializer(mensajes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def enviar_mensaje(request):
    reserva_id = request.data.get('reserva_id')
    contenido = request.data.get('contenido')
    emisor_id = request.data.get('emisor_id')

    if not all([reserva_id, contenido, emisor_id]):
        return Response({'error': 'Faltan datos necesarios'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reserva = Reserva.objects.get(id=reserva_id)
        emisor = User.objects.get(id=emisor_id)

        # Determinar el receptor
        if emisor == reserva.cliente:
            receptor = User.objects.get(is_superuser=True)
        elif emisor.is_superuser:
            receptor = reserva.cliente
        else:
            return Response({'error': 'Receptor no definido'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el mensaje
        mensaje = Mensaje.objects.create(
            reserva=reserva,
            emisor=emisor,
            receptor=receptor,
            contenido=contenido
        )

        # Marcar como respondido si el emisor es el administrador
        if emisor.is_superuser:
            Mensaje.objects.filter(reserva=reserva, respondido=False).update(respondido=True)

        # Asegúrate de que los mensajes no leídos se marquen como leídos
        Mensaje.objects.filter(reserva=reserva, leido=False).update(leido=True)

        return Response(MensajeSerializer(mensaje).data, status=status.HTTP_201_CREATED)

    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_mensajes_leidos(request, reserva_id):
    # Marca los mensajes no leídos de una reserva específica como leídos
    try:
        mensajes = Mensaje.objects.filter(receptor=request.user, reserva_id=reserva_id, leido=False)
        if mensajes.exists():
            mensajes.update(leido=True)  # Actualiza los mensajes a leídos
            return Response({'success': True, 'mensaje': 'Mensajes marcados como leídos'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No hay mensajes no leídos para esta reserva'}, status=status.HTTP_404_NOT_FOUND)
    except Mensaje.DoesNotExist:
        return Response({'error': 'Mensaje no encontrado'}, status=status.HTTP_404_NOT_FOUND)


##################################

@api_view(['POST'])
def marcar_respondido(request, reserva_id):
    try:
        # Filtrar los mensajes no respondidos de una reserva específica
        mensajes = Mensaje.objects.filter(reserva_id=reserva_id, leido=False, respondido=False)
        
        # Si hay mensajes no respondidos, marcarlos como respondidos
        if mensajes.exists():
            mensajes.update(respondido=True)  # Marca como respondido
            return Response({'success': True, 'mensaje': 'Mensajes marcados como respondidos'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No hay mensajes no respondidos para esta reserva'}, status=status.HTTP_404_NOT_FOUND)
    except Mensaje.DoesNotExist:
        return Response({'error': 'Mensaje no encontrado'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def reservas_activas(request):
    # Obtener las reservas activas
    reservas = Reserva.objects.filter(pagado=True, cancelada=False)

    # Obtener los mensajes no leídos para el admin
    mensajes_no_leidos = Mensaje.objects.filter(receptor=request.user, leido=False)

    # Contar los mensajes no respondidos (cambiando la lógica de los mensajes)
    total_mensajes_no_respondidos = mensajes_no_leidos.filter(respondido=False).count()

    return Response({
        'reservas': reservas,
        'total_mensajes_no_respondidos': total_mensajes_no_respondidos
    })



@api_view(['GET'])
def listar_seguimiento_servicios_comunes(request, reserva_id):
    """
    Lista el seguimiento de los servicios comunes asociados a una reserva específica.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Filtra los servicios comunes relacionados con esa reserva
    servicios = ServiciosComunes.objects.filter(reserva=reserva).order_by('dia')

    # Serializa los datos para retornarlos como JSON
    serializer = ServiciosComunesSerializer(servicios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mensajes_no_leidos(request):
    mensajes = Mensaje.objects.filter(receptor=request.user, leido=False).count()
    return Response({'no_leidos': mensajes})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_mensajes_leidos(request, reserva_id):
    Mensaje.objects.filter(receptor=request.user, reserva_id=reserva_id, leido=False).update(leido=True)
    return Response({'success': True})


# class CrearReservaRegalia(APIView):
#     def post(self, request):
#         print('Datos recibidos:', request.data)  # Log para verificar los datos
#         serializer = ReservaRegaliaSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CrearReservaRegalia(APIView):
    def post(self, request):
        # Procesar el objeto recibido
        data = request.data.copy()
        print("Datos recibidos:", data)
        

        # Validar si 'regalia' es un diccionario u objeto, y extraer el ID
        if isinstance(data['regalia'], dict):
            data['regalia'] = data['regalia']['id']  # Extraer solo el ID si es un diccionario

        # Continuar con el flujo normal
        serializer = ReservaRegaliaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errores del serializador:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



##################################

