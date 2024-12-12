import { ReservaRegalia } from "./regalia.model";

export interface User {
  id: number;
  first_name: string;
  email: string;
}

export interface Habitacion {
  id: number;
  numero_habitacion: string;
  precio: number;
}

export interface Mascota {
  id: number;
  nombre_perro: string;
  nombre_dueno: string;
  raza: string;
  edad: number;
  peso: number;
  chip: string;
  comida: string;
  vacunas: string[];
  alergias: string[];
  enfermedades: string[];
  imagen_mascota: string;
}

export interface Reserva {
  id: number;
  cliente: User;
  trabajador: User | null;
  habitacion: Habitacion;
  mascota: Mascota;
  fecha_inicio: string;
  fecha_fin: string;
  precio_total: number;
  pagado: boolean;
  cancelada: boolean;
  check_in: boolean;
  checkout: boolean;
}

export interface ServiciosComunes {
  id: number;
  ficha: number;
  reserva: number;
  comio: boolean;
  paseo: boolean;
  entretencion: boolean;
  medicamentos: boolean;
  fecha_registro: string;
  dia: number;
  observacion: string;
  regalo_evidencia? : string;
  comio_evidencia?: string;
  paseo_evidencia?: string;
  entretencion_evidencia?: string;
  medicamentos_evidencia?: string;
}
