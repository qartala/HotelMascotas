import { Reserva, Mascota } from '../Modelos/reserva.model';

export interface User {
    id: number;
    first_name: string;
    email: string;
  }

export interface Membresia {
    id: number;
    nombre: string;
    descuento: number;
    duracion_dias: number;
    valor: number;
    }

export interface Video {
      id: number; // ID único del video
      cliente: Usuario; // Cliente que subió el video
      reserva: Reserva; // Reserva asociada al video
      ficha: Mascota; // Mascota asociada al video
      archivo_video: string; // URL del video subido
      descripcion?: string; // Descripción del video (opcional)
      fecha_subida: string; // Fecha de subida del video
    }


export interface Usuario {
    idUsuario: User;
    tipo_cuenta: string;
    membresia?: Membresia | null;
    telefono?: string | null;
    direccion?: string | null;
    fecha_nacimiento?: string | null;
    trabajador: boolean;
    fecha_inicio_membresia?: string | null;
    }


export interface Mensaje {
      id: number; // ID único del mensaje
      emisor: {
        id: number; // ID del usuario que envía el mensaje
        first_name: string; // Nombre del usuario que envía el mensaje
      };
      receptor: {
        id: number; // ID del usuario que recibe el mensaje
        first_name: string; // Nombre del usuario que recibe el mensaje
      };
      contenido: string; // Contenido del mensaje
      fecha_hora: string; // Fecha y hora del mensaje en formato ISO (Ej. 2024-11-08T10:30:00Z)
    }



