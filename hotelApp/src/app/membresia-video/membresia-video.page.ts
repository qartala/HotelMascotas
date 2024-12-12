import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { ToastController } from '@ionic/angular';

@Component({
  selector: 'app-membresia-video',
  templateUrl: './membresia-video.page.html',
  styleUrls: ['./membresia-video.page.scss'],
})
export class MembresiaVideoPage {
  reservaId: number = 0; // ID de la reserva
  fichaId: number = 0; // ID de la ficha
  descripcion: string = ''; // Descripción opcional
  videoFile: File | null = null; // Archivo de video seleccionado
  token: string | null = null; // Token para autenticación
  videos: any[] = []; // Lista de videos cargados

  constructor(
    private apiService: ApiService,
    private route: ActivatedRoute,
    private router: Router,
    private toastController: ToastController
  ) {}

  ngOnInit() {
    // Obtener reservaId y fichaId desde la URL
    this.reservaId = Number(this.route.snapshot.paramMap.get('reservaId'));
    this.fichaId = Number(this.route.snapshot.paramMap.get('fichaId'));

    // Obtener el token del almacenamiento local
    this.token = localStorage.getItem('token');

    console.log('Reserva ID:', this.reservaId);
    console.log('Ficha ID:', this.fichaId);

    // Cargar los videos al inicializar el componente
    this.cargarVideos();
  }

  // Manejar la selección de un archivo de video
  seleccionarArchivo(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.videoFile = file;
      console.log('Archivo seleccionado:', file);
    }
  }

  regresar() {
    // Navega de vuelta a la página de reserva-video
    this.router.navigate(['/reserva-video']);
  }

  // Método para mostrar mensajes al usuario
  async presentToast(message: string, color: 'success' | 'danger') {
    const toast = await this.toastController.create({
      message,
      duration: 2000, // Duración de 2 segundos
      color, // Color del mensaje: 'success' o 'danger'
      position: 'top', // Posición del mensaje
    });
    await toast.present();
  }

  // Método para subir el video
  subirVideo() {
    if (!this.videoFile) {
      console.error('No se ha seleccionado un archivo de video.');
      this.presentToast('Por favor, selecciona un archivo de video.', 'danger');
      return;
    }

    if (!this.token) {
      console.error('Token de autenticación no encontrado.');
      this.presentToast('Por favor, inicia sesión nuevamente.', 'danger');
      return;
    }

    // Crear FormData para enviar los datos
    const formData = new FormData();
    formData.append('reserva', this.reservaId.toString()); // ID de la reserva
    formData.append('ficha', this.fichaId.toString()); // ID de la ficha
    formData.append('archivo_video', this.videoFile!); // Archivo de video
    formData.append('descripcion', this.descripcion || ''); // Descripción opcional

    this.apiService.subirVideo(formData).subscribe({
      next: (response) => {
        console.log('Video subido con éxito:', response);
        this.presentToast('¡Video subido exitosamente!', 'success'); // Mostrar mensaje de éxito
        this.cargarVideos(); // Recargar la lista de videos
      },
      error: (err) => {
        console.error('Error al subir el video:', err);
        this.presentToast('Error al subir el video. Inténtalo de nuevo.', 'danger');
      },
    });
  }

  // Método para cargar los videos del usuario
  cargarVideos() {
    this.apiService.getVideosPorReserva(this.reservaId).subscribe({
      next: (response) => {
        console.log('Videos cargados:', response);
        this.videos = response;
      },
      error: (err) => {
        console.error('Error al cargar los videos:', err);
        this.presentToast('Error al cargar los videos.', 'danger');
      },
    });
  }

  // Método para eliminar un video
  eliminarVideo(videoId: number) {
    this.apiService.eliminarVideo(videoId).subscribe({
      next: (response) => {
        console.log('Video eliminado:', response);
        this.presentToast('¡Video eliminado exitosamente!', 'success'); // Mostrar mensaje de éxito
        this.cargarVideos(); // Recargar la lista de videos
      },
      error: (err) => {
        console.error('Error al eliminar el video:', err);
        this.presentToast('Error al eliminar el video. Inténtalo de nuevo.', 'danger');
      },
    });
  }
}
