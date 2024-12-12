import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../servicios/api.service';
import { Reserva, ServiciosComunes } from '../Modelos/reserva.model';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Camera, CameraDirection, CameraSource, CameraResultType } from '@capacitor/camera';
import { AlertController, ToastController } from '@ionic/angular';
import { Regalia, ReservaRegalia } from '../Modelos/regalia.model';

@Component({
  selector: 'app-seguimiento',
  templateUrl: './seguimiento.page.html',
  styleUrls: ['./seguimiento.page.scss'],
})
export class SeguimientoPage {
  reserva: Reserva | undefined;
  servicios: ServiciosComunes[] = [];
  groupedServicios: any[] = [];
  diasReservados: number[] = [];
  private apiUrlServiciosComunes = 'http://localhost:8000/api/servicios-comunes/';
  videoStream: MediaStream | null = null;
  mostrarRegalos: boolean = false;
  reservaRegalia: ReservaRegalia[] = [];
  regalos: Regalia[] = [];

  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
    private router: Router,
    private http: HttpClient,
    private toastController: ToastController,
    private alertController: AlertController
  ) {}

  ionViewWillEnter() {
    const idReserva = Number(this.route.snapshot.paramMap.get('id'));
    if (!isNaN(idReserva)) {
      this.cargarReserva(idReserva);
      this.cargarReservasRegalia(idReserva)
    } else {
      console.warn('ID de reserva inválido');
      this.router.navigate(['/reservas']);
    }
  }

  async presentToast(position: 'top' | 'middle' | 'bottom',mensaje:string) {
    const toast = await this.toastController.create({
      message: mensaje,
      duration: 1500,
      position: position,
    });

    await toast.present();
  }

  cargarReservasRegalia(idReserva: number) {
    this.apiService.cargarReservasRegaliasPorReserva(idReserva).subscribe({
      next: (reservas: ReservaRegalia[]) => {
        // Obtener detalles de regalias directamente
        const reservasConDetalles = reservas.map((reserva) => {
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
          console.log('Reservas con detalles de regalia:', this.reservaRegalia);
        });
      },
      error: (error) => {
        console.error('Error al cargar las reservas de regalias:', error);
        this.router.navigate(['/reservas']); // Redirigir en caso de error
      },
    });
  }

  cargarReserva(idReserva: number) {
    this.apiService.getReserva(idReserva).subscribe(
      (data) => {
        this.reserva = data; // Asignamos la reserva directamente
        this.calcularDiasReservados();
        const idFicha = this.reserva?.mascota.id;
        if (idFicha) {
          this.cargarServiciosComunes(idFicha, idReserva);
        }
      },
      (error) => {
        console.error('Error al obtener la reserva:', error);
        this.router.navigate(['/reservas']);
      }
    );
  }

  calcularDiasReservados() {
    if (this.reserva) {
      const fechaInicio = new Date(this.reserva.fecha_inicio);
      const fechaFin = new Date(this.reserva.fecha_fin);
      const diffTime = Math.abs(fechaFin.getTime() - fechaInicio.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      this.diasReservados = Array.from({ length: diffDays }, (_, i) => i + 1);
    }
  }

  cargarServiciosComunes(idFicha: number, idReserva: number) {
    this.apiService.getServiciosComunes1(idFicha, idReserva).subscribe(
      (data: ServiciosComunes[]) => {
        console.log('Servicios Comunes recibidos del backend:', data);
        this.groupedServicios = this.agruparPorReserva(data);
      },
      (error) => {
        if (error.status === 404) {
          console.warn('No se encontraron servicios comunes.');
        } else {
          console.error('Error al cargar servicios comunes:', error);
        }
      }
    );
  }

  actualizarServicio(idServicio: number, campo: string, valor: string | boolean) {
    const servicioActualizado = { [campo]: valor };
    console.log('Actualizando:', servicioActualizado);

    this.apiService.actualizarServicioComun(idServicio, servicioActualizado).subscribe({
      next: () => console.log(`Servicio ${campo} actualizado a ${valor}`),
      error: (error) => console.error('Error al actualizar el servicio:', error)
    });
  }

  irAVideoTrabajador(reservaId?: number) {
    if (!reservaId) {
      console.error('Reserva ID no definido.');
      return;
    }
    console.log('Navegando a videos del trabajador con ID de reserva:', reservaId);
    this.router.navigate([`/video-trabajador/${reservaId}`]); // Navegación con parámetro dinámico
  }

  async iniciarCamara() {
    try {
      this.videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
    } catch (error) {
      console.error('Error al iniciar la cámara:', error);
    }
  }

  detenerCamara() {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach(track => track.stop());
      this.videoStream = null;
    }
  }

  async capturarEvidencia(servicioId: number, campo: string) {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.DataUrl,
        source: CameraSource.Camera, // Abre directamente la cámara
        direction: CameraDirection.Front // Prioriza la cámara frontal
      });

      if (image && image.dataUrl) {
        const file = this.dataURLtoFile(image.dataUrl, `${campo}.jpg`);
        if (file) {
          this.subirEvidencia(servicioId, campo, file);
        } else {
          console.error("Error: No se pudo convertir la imagen a un archivo.");
        }
      }
    } catch (error) {
      console.error('Error al capturar la imagen:', error);
    }
  }

  dataURLtoFile(dataUrl: string, filename: string): File | null {
    const arr = dataUrl.split(',');
    const match = arr[0].match(/:(.*?);/);
    const mime = match ? match[1] : null;

    if (!mime) {
      console.error("Error: El tipo MIME no se pudo determinar.");
      return null;
    }

    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }

    return new File([u8arr], filename, { type: mime });
  }

  subirEvidencia(servicioId: number, campo: string, file: File) {
    const url = `${this.apiUrlServiciosComunes}${servicioId}/subir-evidencia/${campo}/`;
    const formData = new FormData();
    formData.append('file', file);

    this.http.post(url, formData, {
      headers: new HttpHeaders({ 'Authorization': `Bearer ${this.getToken()}` })
    }).subscribe({
      next: (response) => this.presentToast("top", "evidencia subida con exito"),
      error: (error) => this.presentToast("top", "La evidencia no se ha podido subir")
    });
  }

  getToken(): string | null {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No se encontró el token.');
    }
    return token;
  }

  volver() {
    this.router.navigate(['/reservas']);
  }


  agruparPorReserva(servicios: ServiciosComunes[]) {
    const grouped: { reserva: number; dias: ServiciosComunes[] }[] = [];

    servicios.forEach(servicio => {
      let grupo = grouped.find(g => g.reserva === servicio.reserva);

      if (!grupo) {
        grupo = { reserva: servicio.reserva, dias: [] };
        grouped.push(grupo);
      }

      grupo.dias.push(servicio);
    });

    return grouped;
  }

  toggleRegalos(): void {
    this.mostrarRegalos = !this.mostrarRegalos; // Alternar visibilidad
    console.log(this.mostrarRegalos ? 'Mostrando regalos' : 'Ocultando regalos'); // Mensaje de depuración opcional
  }

  async confirmarUso(reservaRegalia: any) {
    const alert = await this.alertController.create({
      header: 'Confirmar Uso',
      message: `¿Deseas marcar este regalo como entregado?`,
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
          text: 'Confirmar',
          handler: () => {
            this.marcarComoUsado(reservaRegalia);
          },
        },
      ],
    });

    await alert.present();
  }

  marcarComoUsado(reservaRegalia: any) {
    const data = {
      id: reservaRegalia.id,
      usada: true, // Cambiar el estado a true
    };

    this.apiService.modificarReservaRegalia(data).subscribe({
      next: (response) => {
        console.log('Estado actualizado en el backend:', response);

        // Actualiza la vista local
        reservaRegalia.usada = true;

        this.presentToast('top', 'El regalo fue marcado como utilizado');
      },
      error: (error) => {
        console.error('Error al actualizar el estado:', error);
        this.presentToast('top', 'No se pudo marcar el regalo como utilizado');
      },
    });
  }
}
