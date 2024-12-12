import { User } from "./reserva.model";
import { Reserva } from "./reserva.model";

export interface Regalia {
  id: number;
  nombre: string;
  foto: string;
  descripcion: string;
  precio: number;
  stock: number;
}

export interface ReservaRegalia {
  id: number;
  cliente: User;
  reserva: Reserva;
  regalia: Regalia;
  cantidad: number;
  precio_total_r: number;
  fecha: string;
  pagada: boolean;
  usada: boolean;
}
