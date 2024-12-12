import { Component } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { Regalia, ReservaRegalia } from '../Modelos/regalia.model';
import { Reserva } from '../Modelos/reserva.model';
import { AlertController, ToastController } from '@ionic/angular';

@Component({
  selector: 'app-regalia-usuario',
  templateUrl: './regalia-usuario.page.html',
  styleUrls: ['./regalia-usuario.page.scss'],
})
export class RegaliaUsuarioPage {
  reservaRegalia: ReservaRegalia[] = [];
  reservasActivas: Reserva[] = []; // Todas las reservas activas

  constructor(private apiService: ApiService, private router: Router,private alertController: AlertController,private toastController: ToastController) {}

  ionViewWillEnter() {
    const idUsuario = this.getUsuarioId();
    this.cargarReservasRegalias(idUsuario);
    this.cargarReservasActivas(idUsuario);
  }

  cargarReservasRegalias(idUsuario: number) {
    this.apiService.cargarReservasRegaliasUsuario(idUsuario).subscribe({
      next: (reservas: ReservaRegalia[]) => {
        // Filtrar reservas donde el campo `reserva` es null o undefined
        const reservasFiltradas = reservas.filter((reserva) => !reserva.reserva);

        // Obtener detalles de regalias solo para las reservas filtradas
        const reservasConDetalles = reservasFiltradas.map((reserva) => {
          return this.apiService
            .obtenerRegaliaPorId(reserva.regalia)
            .toPromise()
            .then((regaliaDetalles) => {
              if (regaliaDetalles) {
                reserva.regalia = regaliaDetalles; // Asignar detalles completos de la regalia
              } else {
                console.warn(`No se encontraron detalles para la regalia con ID ${reserva.regalia.id}`);
              }
              return reserva;
            });
        });

        // Esperar a que se resuelvan todas las promesas
        Promise.all(reservasConDetalles).then((reservasConRegalias) => {
          this.reservaRegalia = reservasConRegalias;
          console.log('Reservas con detalles de regalia (y sin reserva asociada):', this.reservaRegalia);
        });
      },
      error: (error) => {
        console.error('Error al cargar las reservas:', error);
      },
    });
  }

  cargarReservasActivas(idUsuario: number) {
    this.apiService.getReservas().subscribe({
      next: (reservas: Reserva[]) => {
        // Filtrar reservas activas
        this.reservasActivas = reservas.filter(
          (reserva) =>
            reserva.cliente.id === idUsuario &&
            reserva.check_in === true &&
            reserva.checkout === false
        );
        console.log('Reservas activas:', this.reservasActivas);
      },
      error: (error) => {
        console.error('Error al cargar las reservas activas:', error);
      },
    });
  }

  async confirmarEnvio(reservaActiva: Reserva, reservaRegalia: ReservaRegalia) {
    const alert = await this.alertController.create({
      header: 'Confirmar Envío',
      message: `¿Deseas enviar el regalo a esta reserva?`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'secondary',
          handler: () => {
            console.log('Acción cancelada');
          },
        },
        {
          text: 'Enviar',
          handler: () => {
            this.enviarReserva(reservaActiva, reservaRegalia);
          },
        },
      ],
    });

    await alert.present();
  }


  enviarReserva(reservaActiva: Reserva, reservaRegalia: ReservaRegalia) {
    console.log('Reserva activa:', reservaActiva);
    console.log('Reserva de regalia:', reservaRegalia);

    // Construir los datos para actualizar ReservaRegalia
    const data = {
      id: reservaRegalia.id,
      reserva: reservaActiva.id,
    };

    // Llamar al método del servicio para modificar la ReservaRegalia
    this.apiService.modificarReservaRegalia(data).subscribe({
      next: (response) => {
        console.log('ReservaRegalia actualizada exitosamente:', response);
        this.presentToast('top','Regalo enviado, se encargaran de entregarlo a su mascota');
        this.regresar();
      },
      error: (error) => {
        console.error('Error al actualizar ReservaRegalia:', error);
        this.presentToast('top','No se pudo enviar el regalo correctamente');
        this.regresar();
      },
    });
  }

  async presentToast(position: 'top' | 'middle' | 'bottom',mensaje:string) {
    const toast = await this.toastController.create({
      message: mensaje,
      duration: 3000,
      position: position,
    });

    await toast.present();
  }

  getReservasPorRegalia(): Reserva[] {
    return this.reservasActivas;
  }

  getUsuarioId() {
    const usuario = localStorage.getItem('usuario');
    if (usuario) {
      try {
        const usuarioObj = JSON.parse(usuario);
        return usuarioObj.id;
      } catch (error) {
        console.error('Error al parsear el usuario:', error);
      }
    }
    return null;
  }

  regresar() {
    this.router.navigate(['/home']);
  }
}
