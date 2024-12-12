import { Component, OnInit } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Reserva } from '../Modelos/reserva.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-reservas',
  templateUrl: './reservas.page.html',
  styleUrls: ['./reservas.page.scss'],
})
export class ReservasPage {

  reservas: Reserva[] = [];
  filtro: string = '';

  constructor(private apiService: ApiService, private router: Router) {}

  ionViewWillEnter() {
    this.verificarUsuarioTrabajador();
  }

  // Verificar si el usuario es trabajador y cargar reservas
  verificarUsuarioTrabajador() {
    this.apiService.getUsuarioData().subscribe({
      next: (usuario) => {
        if (usuario && usuario.trabajador) {
          console.log('Usuario es trabajador, cargando reservas.');
          this.cargarReservas();  // Cargar reservas si es trabajador
        } else {
          console.warn('El usuario no es trabajador. Redirigiendo a Home.');
          this.router.navigate(['/home']);  // Redirigir a home si no es trabajador
        }
      },
      error: (error) => {
        console.error('Error al obtener datos del usuario:', error);
        this.router.navigate(['/login']);
      }
    });
  }


  cargarReservas() {
    this.apiService.getReservas().subscribe({
      next: (data: Reserva[]) => {
        // Filtrar reservas para excluir las que tienen checkout en true
        this.reservas = data.filter(reserva => !reserva.checkout);

  
        console.log('Reservas cargadas y filtradas:', this.reservas);
      },
      error: (error) => {
        console.error('Error al cargar las reservas:', error);
      }
    });
  }
  


  get reservasFiltradas() {
    return this.reservas.filter((reserva) => {
      const clienteUsername = reserva.cliente?.first_name?.toLowerCase() || '';
      const numeroHabitacion = reserva.habitacion?.numero_habitacion || '';
      return (
        clienteUsername.includes(this.filtro.toLowerCase()) ||
        numeroHabitacion.includes(this.filtro)
      );
    });
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
      }
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
      }
    });
  }

  verSeguimiento(id: number) {
    this.router.navigate([`/seguimiento`, id]);
  }

}
