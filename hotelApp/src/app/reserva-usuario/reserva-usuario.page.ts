import { Component } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Reserva } from '../Modelos/reserva.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-reserva-usuario',
  templateUrl: './reserva-usuario.page.html',
  styleUrls: ['./reserva-usuario.page.scss'],
})
export class ReservaUsuarioPage {
  reservas: Reserva[] = [];
  reservasFiltradas: Reserva[] = []; // Lista de reservas filtradas
  usuario: any;
  filtro: string = '';

  constructor(private apiService: ApiService, private router: Router) {}

  ionViewWillEnter() {
    this.verificarUsuario();
  }

  // Verificar si el usuario es trabajador y cargar reservas
  verificarUsuario() {
    this.apiService.getUsuarioData().subscribe({
      next: (usuario) => {
        if (usuario) {
          if (usuario.trabajador) {
            console.log('Usuario es trabajador, cargando todas las reservas.');
            this.cargarReservas(); // Cargar todas las reservas si es trabajador
          } else {
            console.log('Usuario no es trabajador, cargando sus reservas activas.');
            this.cargarPerfil(); // Cargar reservas activas del usuario
          }
        } else {
          console.warn('No se encontró al usuario. Redirigiendo a login.');
          this.router.navigate(['/login']);
        }
      },
      error: (error) => {
        console.error('Error al obtener datos del usuario:', error);
        this.router.navigate(['/login']);
      },
    });
  }

  // Cargar reservas para trabajadores
  cargarReservas() {
    this.apiService.getReservas().subscribe({
      next: (data: Reserva[]) => {
        this.reservas = data
          .filter((reserva) => !reserva.checkout) // Excluir reservas con check_out = true
          .sort(
            (a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
          );
        this.reservasFiltradas = this.reservas; // Inicializar reservas filtradas
        console.log('Reservas cargadas:', this.reservas);
      },
      error: (error) => {
        console.error('Error al cargar las reservas:', error);
      },
    });
  }

  // Cargar reservas activas para el usuario no trabajador
  cargarReservasUsuario(userId: number) {
    this.apiService.getReservasPorUsuario(userId).subscribe({
      next: (data: Reserva[]) => {
        this.reservas = data
          .filter((reserva) => !reserva.cancelada && !reserva.checkout) // Excluir check_out = true
          .sort(
            (a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
          );
        this.reservasFiltradas = this.reservas; // Inicializar reservas filtradas
        console.log('Reservas activas cargadas para el usuario:', this.reservas);
      },
      error: (error) => {
        console.error('Error al cargar las reservas del usuario:', error);
      },
    });
  }

  cargarPerfil() {
    this.apiService.getUsuarioPerfil().subscribe({
      next: (data) => {
        this.usuario = data;
        this.cargarReservasUsuario(this.usuario.idUsuario.id);
        console.log('Datos del perfil:', data);
      },
      error: (error) => {
        console.error('Error al cargar el perfil:', error);
      },
    });
  }

  // Método para filtrar reservas dinámicamente
  filtrarReservas() {
    this.reservasFiltradas = this.reservas.filter(
      (reserva) =>
        !reserva.checkout && // Excluir reservas con check_out = true
        (reserva.mascota?.nombre_perro?.toLowerCase().includes(this.filtro.toLowerCase()) ||
          reserva.habitacion?.numero_habitacion?.toString().includes(this.filtro))
    );
  }

  regresar() {
    this.router.navigate(['/home']);
  }

  actualizarCheckIn(reserva: Reserva) {
    const nuevaReserva: Partial<Reserva> = { check_in: !reserva.check_in };

    this.apiService.actualizarReservaCheckIn(reserva.id, nuevaReserva).subscribe({
      next: (response) => {
        console.log(`Check-in actualizado para la reserva ${reserva.id}.`);
        this.cargarReservas();
      },
      error: (error) => {
        console.error('Error al actualizar el check-in:', error);
      },
    });
  }

  actualizarPagado(reserva: Reserva) {
    const nuevoEstado = !reserva.pagado;

    this.apiService.actualizarEstadoPagado(reserva.id, nuevoEstado).subscribe({
      next: (response) => {
        console.log(`Estado de pago actualizado para la reserva ${reserva.id}.`);
        this.cargarReservas();
      },
      error: (error) => {
        console.error('Error al actualizar el estado de pago:', error);
      },
    });
  }

  verSeguimientoUsuario(id: number) {
    this.router.navigate([`/seguimiento-usuario`, id]);
  }
}
