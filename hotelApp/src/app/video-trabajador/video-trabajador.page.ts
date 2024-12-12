import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../servicios/api.service';
import { ToastController } from '@ionic/angular';


@Component({
  selector: 'app-video-trabajador',
  templateUrl: './video-trabajador.page.html',
  styleUrls: ['./video-trabajador.page.scss'],
})
export class VideoTrabajadorPage implements OnInit {
  reservaId: number = 0; // ID de la reserva
  videos: any[] = []; // Lista de videos asociados a la reserva

  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
    private router: Router,
    private toastController: ToastController // Añadir esta línea
  ) {}


ngOnInit() {
  const reservaIdParam = this.route.snapshot.paramMap.get('reservaId');
  if (reservaIdParam) {
    this.reservaId = Number(reservaIdParam);
    console.log('Reserva ID capturado:', this.reservaId);
    this.cargarVideosPorReserva();
  } else {
    console.error('No se encontró reservaId en la ruta.');
    this.router.navigate(['/seguimiento']);
  }
}



  regresar() {
    // Regresar al seguimiento utilizando el ID de la reserva
    this.router.navigate([`/seguimiento/${this.reservaId}`]);
  }

  cargarVideosPorReserva() {
    console.log('Cargando videos para la reserva ID:', this.reservaId); // Log para depuración

    this.apiService.getVideosPorReserva(this.reservaId).subscribe({
      next: (response) => {
        console.log(`Videos cargados para la reserva ${this.reservaId}:`, response);
        this.videos = response;
      },
      error: (err) => {
        console.error(`Error al cargar los videos para la reserva ${this.reservaId}:`, err);
        this.presentToast(err.message, 'danger'); // Notificar al usuario
      },
    });
  }

  async presentToast(message: string, color: 'success' | 'danger') {
    const toast = await this.toastController.create({
      message,
      duration: 2000,
      color,
      position: 'top',
    });
    await toast.present();
  }


}
