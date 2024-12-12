from rest_framework import serializers
from modulo.Producto.models import Reserva, Habitacion, Regalia, Membresia, ReservaRegalia,Video
from modulo.Usuario.models import Ficha, Usuario, ServiciosComunes, Mensaje
from django.contrib.auth.models import User


class VideoUploadSerializer(serializers.ModelSerializer):
    archivo_video = serializers.FileField()

    class Meta:
        model = Video
        fields = ['reserva', 'ficha', 'archivo_video', 'descripcion']

    def validate(self, data):
        usuario = self.context['request'].user.usuario  # Usuario autenticado
        reserva = data.get('reserva')  # Instancia de Reserva
        ficha = data.get('ficha')  # Instancia de Ficha

        # Verificar que la reserva pertenece al cliente autenticado
        if reserva.cliente != usuario.idUsuario:
            raise serializers.ValidationError("La reserva no pertenece al usuario autenticado.")

        # Verificar que la ficha pertenece al cliente autenticado
        if ficha.id_usuario != usuario:
            raise serializers.ValidationError("La ficha no pertenece al usuario autenticado.")

        return data

    def create(self, validated_data):
        # Asignar el cliente autenticado al video
        validated_data['cliente'] = self.context['request'].user.usuario
        return super().create(validated_data)



class VideoListSerializer(serializers.ModelSerializer):
    ficha = serializers.CharField(source='ficha.nombre_perro', read_only=True)
    reserva = serializers.CharField(source='reserva.id', read_only=True)
    archivo_video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'ficha', 'reserva', 'archivo_video_url', 'descripcion', 'fecha_subida']

    def get_archivo_video_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.archivo_video.url)



class UserSerializer(serializers.ModelSerializer):
    """Serializador para datos básicos del usuario."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para datos extendidos del usuario."""
    idUsuario = UserSerializer()  # Datos anidados del usuario

    class Meta:
        model = Usuario
        fields = [
            'idUsuario', 'tipo_cuenta', 'telefono', 'direccion',
            'fecha_nacimiento', 'membresia', 'fecha_inicio_membresia', 'trabajador'
        ]


class MensajeSerializer(serializers.ModelSerializer):
    emisor_nombre = serializers.SerializerMethodField()
    receptor_nombre = serializers.CharField(source='receptor.first_name', read_only=True)

    class Meta:
        model = Mensaje
        fields = ['id', 'reserva', 'emisor', 'emisor_nombre', 'receptor', 'receptor_nombre', 'contenido', 'fecha_hora']

    def get_emisor_nombre(self, obj):
        if obj.emisor.is_superuser:
            return "PetsTeam"
        return obj.emisor.first_name or obj.emisor.username


class MembresiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membresia
        fields = ['id', 'nombre', 'descuento', 'duracion_dias', 'valor']


class HabitacionSerializer(serializers.ModelSerializer):
    """Serializador para habitaciones."""
    class Meta:
        model = Habitacion
        fields = ['id', 'numero_habitacion', 'precio']


class FichaSerializer(serializers.ModelSerializer):
    """Serializador para fichas de mascotas."""
    vacunas = serializers.SerializerMethodField()
    alergias = serializers.SerializerMethodField()
    enfermedades = serializers.SerializerMethodField()

    class Meta:
        model = Ficha
        fields = [
            'id', 'nombre_perro', 'nombre_dueno', 'raza', 'edad',
            'peso', 'chip', 'comida', 'vacunas', 'alergias',
            'enfermedades', 'imagen_mascota'
        ]

    def get_vacunas(self, obj):
        return obj.get_vacunas()

    def get_alergias(self, obj):
        return obj.get_alergias()

    def get_enfermedades(self, obj):
        return obj.get_enfermedades()


class ReservaSerializer(serializers.ModelSerializer):
    cliente = UserSerializer()  # Datos del cliente
    habitacion = HabitacionSerializer()  # Datos de la habitación
    mascota = FichaSerializer()  # Datos de la mascota

    class Meta:
        model = Reserva
        fields = [
            'id', 'cliente', 'habitacion', 'mascota',
            'fecha_inicio', 'fecha_fin', 'precio_total',
            'pagado', 'cancelada', 'check_in','checkout'
        ]



class ServiciosComunesSerializer(serializers.ModelSerializer):
    """Serializador para servicios comunes."""
    class Meta:
        model = ServiciosComunes
        fields = [
            'id', 'ficha', 'reserva', 'comio', 'paseo', 'entretencion', 'medicamentos',
            'observacion', 'fecha_registro', 'dia',
            'comio_evidencia', 'paseo_evidencia', 'entretencion_evidencia', 'medicamentos_evidencia', 'regalo_evidencia'
        ]


class RegaliaSerializer(serializers.ModelSerializer):
    """Serializador para regalias."""
    class Meta:
        model = Regalia
        fields = ['id', 'nombre', 'foto', 'descripcion', 'precio', 'stock']



class ReservaRegaliaSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    regalia = serializers.PrimaryKeyRelatedField(queryset=Regalia.objects.all())
    reserva = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(),
        required=False,  # Hacer que el campo no sea obligatorio
        allow_null=True  # Permitir valores null
    )

    class Meta:
        model = ReservaRegalia
        fields = ['id', 'cliente', 'regalia', 'reserva', 'cantidad', 'precio_total_r', 'fecha', 'pagada', 'usada']
        