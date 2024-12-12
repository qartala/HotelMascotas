import { Component, OnInit } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { Reserva } from '../Modelos/reserva.model';

@Component({
  selector: 'app-reserva-video',
  templateUrl: './reserva-video.page.html',
  styleUrls: ['./reserva-video.page.scss'],
})
export class ReservaVideoPage implements OnInit {
  reservas: Reserva[] = [];
  reservasFiltradas: Reserva[] = [];
  filtro: string = '';
  usuarioEsTrabajador: boolean = false;

  constructor(private apiService: ApiService, private router: Router) {}

  ngOnInit() {
    this.verificarUsuario();
  }

  // Verificar si el usuario es trabajador o cliente
  verificarUsuario() {
    this.apiService.getUsuarioPerfil().subscribe({
      next: (usuario) => {
        if (usuario) {
          this.usuarioEsTrabajador = usuario.trabajador === 1;

          if (this.usuarioEsTrabajador) {
            console.log('Usuario es trabajador, cargando todas las reservas.');
            this.cargarReservasTrabajador();
          } else {
            console.log('Usuario no es trabajador, cargando sus reservas activas.');
            this.cargarReservasCliente(usuario.idUsuario.id);
          }
        } else {
          console.warn('Usuario no encontrado. Redirigiendo a login.');
          this.router.navigate(['/login']);
        }
      },
      error: (err) => {
        console.error('Error al verificar usuario:', err);
        this.router.navigate(['/login']);
      },
    });
  }

  // Cargar reservas para clientes (solo reservas activas)
  cargarReservasCliente(clienteId: number) {
    this.apiService.getReservasPorUsuario(clienteId).subscribe({
      next: (reservas) => {
        this.reservas = reservas.filter((reserva) => !reserva.cancelada);
        this.reservasFiltradas = [...this.reservas];
        console.log('Reservas activas para el cliente:', this.reservas);
      },
      error: (err) => {
        console.error('Error al cargar reservas para el cliente:', err);
      },
    });
  }

  // Cargar todas las reservas para el trabajador
  cargarReservasTrabajador() {
    this.apiService.getReservas().subscribe({
      next: (reservas) => {
        this.reservas = reservas;
        this.reservasFiltradas = [...this.reservas];
        console.log('Reservas cargadas para el trabajador:', this.reservas);
      },
      error: (err) => {
        console.error('Error al cargar reservas para el trabajador:', err);
      },
    });
  }

  // Filtrar reservas por texto
  filtrarReservas() {
    this.reservasFiltradas = this.reservas.filter(
      (reserva) =>
        reserva.mascota?.nombre_perro
          ?.toLowerCase()
          .includes(this.filtro.toLowerCase()) ||
        reserva.habitacion?.numero_habitacion
          ?.toString()
          .includes(this.filtro)
    );
  }

  // Redirigir a la página de videos
// Redirigir a la página de videos con reserva y ficha
irAVideos(reserva: any) {
  this.router.navigate([`/membresia-video`, reserva.id, reserva.mascota.id]);
}


  regresar() {
    this.router.navigate(['/home']);
  }
}
