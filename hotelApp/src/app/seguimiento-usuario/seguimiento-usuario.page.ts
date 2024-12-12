import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../servicios/api.service';
import { Reserva, ServiciosComunes } from '../Modelos/reserva.model';
import { HttpClient } from '@angular/common/http';
import { ReservaRegalia } from '../Modelos/regalia.model';

@Component({
  selector: 'app-seguimiento-usuario',
  templateUrl: './seguimiento-usuario.page.html',
  styleUrls: ['./seguimiento-usuario.page.scss'],
})
export class SeguimientoUsuarioPage {
  reserva: Reserva | undefined;
  serviciosComunes: ServiciosComunes[] = [];
  groupedServicios: any[] = [];
  diasReservados: number[] = [];
  private apiUrlServiciosComunes = 'http://localhost:8000/api/servicios-comunes/';
  private apiUrlReserva = 'http://localhost:8000/api/reservas/';
  videoStream: MediaStream | null = null;
  reservaId: number = 0; // ID de la reserva
  reservaRegalia: ReservaRegalia[] = [];

  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
    private router: Router,
    private http: HttpClient
  ) {}

  ionViewWillEnter() {
    this.route.params.subscribe((params) => {
      this.reservaId = +params['reservaId'];
      if (!isNaN(this.reservaId)) {
        this.verificarCheckIn(this.reservaId); // Verificar el check-in antes de cargar servicios
        this.cargarReservasRegalia(this.reservaId)
      } else {
        console.warn('ID de reserva inválido');
      }
    });
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

  verificarCheckIn(reservaId: number) {
    const url = `${this.apiUrlReserva}${reservaId}/`; // Endpoint para obtener la reserva
    this.http.get<any>(url).subscribe(
      (reserva) => {
        if (reserva.check_in) {
          this.reserva = reserva; // Guardar la reserva
          this.calcularDiasReservados(reserva.fecha_inicio, reserva.fecha_fin); // Calcular días reservados
          this.cargarServiciosComunes(reservaId); // Cargar los servicios comunes
        } else {
          console.warn('El check-in no está realizado. No se puede mostrar el seguimiento.');
          this.router.navigate(['/reservas-usuario']); // Redirige a la lista de reservas
        }
      },
      (error) => {
        console.error('Error al verificar el check-in:', error);
        this.router.navigate(['/reservas-usuario']); // Redirige en caso de error
      }
    );
  }

  calcularDiasReservados(fechaInicio: string, fechaFin: string) {
    const startDate = new Date(fechaInicio);
    const endDate = new Date(fechaFin);
    const diasReservados: any[] = [];
    let currentDate = new Date(startDate);
    let dia = 1;

    while (currentDate <= endDate) {
      diasReservados.push({
        dia: `Día ${dia}`,
        fecha: currentDate.toISOString().split('T')[0], // Formato YYYY-MM-DD
        servicios: [], // Aquí se cargarán los servicios más tarde
      });

      currentDate.setDate(currentDate.getDate() + 1); // Avanzar al siguiente día
      dia++;
    }

    this.groupedServicios = diasReservados; // Guardar los días en el componente
  }


  cargarServiciosComunes(reservaId: number) {
    this.apiService.getServiciosComunes(reservaId).subscribe(
      (data) => {
        // Mapear y organizar los servicios comunes
        this.serviciosComunes = data.map((servicio) => {
          // Construir URLs completas de evidencias
          servicio.comio_evidencia = servicio.comio_evidencia
            ? this.apiService.getMediaUrl(servicio.comio_evidencia)
            : '';
          servicio.entretencion_evidencia = servicio.entretencion_evidencia
            ? this.apiService.getMediaUrl(servicio.entretencion_evidencia)
            : '';
          servicio.paseo_evidencia = servicio.paseo_evidencia
            ? this.apiService.getMediaUrl(servicio.paseo_evidencia)
            : '';
          servicio.medicamentos_evidencia = servicio.medicamentos_evidencia
            ? this.apiService.getMediaUrl(servicio.medicamentos_evidencia)
            : '';
          servicio.regalo_evidencia = servicio.regalo_evidencia
            ? this.apiService.getMediaUrl(servicio.regalo_evidencia)
            : '';

          return servicio; // Devolver servicio con URLs procesadas
        });

        // Agrupar servicios por día
        this.groupedServicios = this.agruparServiciosPorDia(this.serviciosComunes);
      },
      (error) => {
        console.error('Error al obtener servicios comunes:', error);
      }
    );
  }



  agruparServiciosPorDia(servicios: ServiciosComunes[]): any[] {
    const agrupados = servicios.reduce((acc: { [key: string]: ServiciosComunes[] }, servicio) => {
      const fecha = servicio.fecha_registro; // Usar fecha del servicio
      if (!acc[fecha]) {
        acc[fecha] = [];
      }
      acc[fecha].push(servicio);
      return acc;
    }, {});

    // Convertir a un array con día y fecha
    return Object.entries(agrupados).map(([fecha, servicios], index) => ({
      dia: `Día ${index + 1}`,
      fecha, // Asignar la fecha
      servicios,
    }));
  }

  ir(url: string) {
    this.router.navigate([`/${url}`]);
  }

  irAlChat() {
    if (this.reservaId) {
      this.router.navigate([`/chat-usuario/${this.reservaId}`]); // Redirige al chat del usuario
    } else {
      console.error('No hay reserva disponible para el chat.');
    }
  }
}
